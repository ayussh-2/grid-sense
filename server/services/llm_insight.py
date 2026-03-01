import asyncio
import json
import re
import time
import traceback
from typing import Literal, Optional
from pathlib import Path
from pydantic import BaseModel, Field
from google import genai
from services.devices import device_manager
from services.grid_context import grid_context_service
from services.pathway.config import PathwayConfig


class GridInsight(BaseModel):
    summary: str = Field(description="2-3 sentence natural language overview of current grid and device state.")
    severity: Literal["normal", "warning", "critical"] = Field(description="Overall severity: normal if stable, warning if approaching limits, critical if faults or overcurrent.")
    observations: list[str] = Field(description="3-5 key observations about device behavior, grid conditions, and anomalies.")
    actions: list[str] = Field(description="1-3 specific recommended actions the operator should take right now.")
    cost_insight: str = Field(description="One sentence about current energy cost situation.")
    carbon_insight: str = Field(description="One sentence about current carbon/sustainability situation.")


SYSTEM_PROMPT = """You are GridSense AI, an energy monitoring assistant for an industrial facility.
You analyze real-time device telemetry, grid conditions, and anomaly data to provide operators with clear, actionable insights.

Rules:
- Be specific: reference device IDs, exact current/power values, and dollar amounts.
- Be concise: operators need quick answers, not essays.
- Prioritize safety: faults and overcurrent come before cost optimization.
- If devices are off, say so plainly. Don't invent problems.
- If grid pricing is HIGH, suggest deferring non-critical loads.
- If carbon is HIGH, mention sustainability impact.
- Never use emojis."""

CRITICAL_MONITOR_INTERVAL = 2.0
CURRENT_BUCKET_SIZE = 10.0


def _build_context() -> str:
    telemetry = device_manager.get_all_telemetry()
    grid = grid_context_service.get_context()

    total_current = sum(d["current"] for d in telemetry.values())
    total_power = sum(d["power"] for d in telemetry.values())
    faults = [d for d in telemetry.values() if d["status"] == "fault"]

    lines = [
        "=== DEVICE TELEMETRY ===",
        f"Total current: {total_current:.1f}A | Total power: {total_power:.0f}W",
    ]
    for d in telemetry.values():
        lines.append(f"  {d['device_id']} ({d['device_type']}): status={d['status']}, current={d['current']:.1f}A, power={d['power']:.0f}W")

    if faults:
        lines.append(f"\nACTIVE FAULTS: {len(faults)} device(s) in fault state")
        for f in faults:
            lines.append(f"  >> {f['device_id']}: FAULT at {f['current']:.1f}A / {f['power']:.0f}W -- IMMEDIATE ACTION REQUIRED")

    lines.append("\n=== GRID CONTEXT ===")
    lines.append(f"  Carbon intensity: {grid.get('carbon_intensity', 0):.0f} gCO2/kWh ({grid.get('carbon_level', 'UNKNOWN')})")
    lines.append(f"  Electricity price: ${grid.get('electricity_price', 0):.4f}/kWh ({grid.get('pricing_tier', 'UNKNOWN')})")
    lines.append(f"  Renewable energy: {grid.get('grid_renewable_percentage', 0):.0f}%")

    anomalies_file = Path(PathwayConfig.ANOMALIES_FILE)
    stats_file = Path(PathwayConfig.DEVICE_STATS_FILE)

    if anomalies_file.exists():
        try:
            with open(anomalies_file) as f:
                recent = f.readlines()[-5:]
            lines.append("\n=== PATHWAY ANOMALIES (last 5) ===")
            for raw in recent:
                try:
                    a = json.loads(raw)
                    if a.get("diff", 1) > 0:
                        lines.append(f"  {a.get('device_id','?')}: {a.get('alert','?')} ({a.get('current',0):.1f}A)")
                except json.JSONDecodeError:
                    pass
        except Exception:
            pass

    if stats_file.exists():
        try:
            with open(stats_file) as f:
                stat_lines = f.readlines()[-10:]
            latest_stats = {}
            for raw in stat_lines:
                try:
                    s = json.loads(raw)
                    if s.get("diff", 1) > 0:
                        latest_stats[s["device_type"]] = s
                except (json.JSONDecodeError, KeyError):
                    pass
            if latest_stats:
                lines.append("\n=== PATHWAY DEVICE STATISTICS ===")
                for dt, s in latest_stats.items():
                    lines.append(f"  {dt}: avg={s.get('avg_current',0):.1f}A, max={s.get('max_current',0):.1f}A, samples={s.get('total_samples',0)}")
        except Exception:
            pass

    return "\n".join(lines)


def _compute_state_fingerprint() -> str:
    telemetry = device_manager.get_all_telemetry()
    grid = grid_context_service.get_context()

    parts = []
    for d in sorted(telemetry.values(), key=lambda x: x["device_id"]):
        current_bucket = int(d["current"] / CURRENT_BUCKET_SIZE)
        parts.append(f"{d['device_id']}:{d['status']}:{current_bucket}")

    parts.append(f"price:{grid.get('pricing_tier', '?')}")
    parts.append(f"carbon:{grid.get('carbon_level', '?')}")
    return "|".join(parts)


def _detect_critical_state() -> bool:
    telemetry = device_manager.get_all_telemetry()
    for d in telemetry.values():
        if d["status"] == "fault":
            return True
        if d["current"] > PathwayConfig.HIGH_CURRENT_THRESHOLD:
            return True
    return False


def _parse_retry_delay(error: Exception) -> Optional[float]:
    msg = str(error)
    match = re.search(r"retry in ([\d.]+)s", msg, re.IGNORECASE)
    if match:
        return float(match.group(1))
    return None


class LLMInsightService:
    def __init__(self):
        self._client: Optional[genai.Client] = None
        self._run_task: Optional[asyncio.Task] = None
        self._monitor_task: Optional[asyncio.Task] = None
        self.latest_insight: Optional[dict] = None
        self._interval = PathwayConfig.LLM_INSIGHT_INTERVAL
        self._urgent = asyncio.Event()
        self._last_fingerprint: Optional[str] = None
        self._backoff_until: float = 0.0
        self.version = 0

    def _get_client(self) -> genai.Client:
        if self._client is None:
            self._client = genai.Client(api_key=PathwayConfig.GEMINI_API_KEY)
        return self._client

    def trigger_urgent(self):
        self._urgent.set()

    async def generate_insight(self) -> dict:
        context = _build_context()
        client = self._get_client()

        response = await asyncio.to_thread(
            client.models.generate_content,
            model=PathwayConfig.GEMINI_MODEL,
            contents=f"Analyze this grid snapshot and provide your insight:\n\n{context}",
            config={
                "system_instruction": SYSTEM_PROMPT,
                "response_mime_type": "application/json",
                "response_json_schema": GridInsight.model_json_schema(),
            },
        )

        parsed = GridInsight.model_validate_json(response.text)
        result = {**parsed.model_dump(), "timestamp": time.time()}
        self.version += 1
        return result

    async def _try_generate(self) -> bool:
        now = time.time()
        if now < self._backoff_until:
            return False

        fingerprint = _compute_state_fingerprint()
        is_urgent = self._urgent.is_set()

        if fingerprint == self._last_fingerprint and not is_urgent:
            return False

        try:
            self.latest_insight = await self.generate_insight()
            self._last_fingerprint = fingerprint
            print(f"LLM insight: severity={self.latest_insight['severity']}")
            return True
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                retry_delay = _parse_retry_delay(e) or 60.0
                self._backoff_until = time.time() + retry_delay
                print(f"LLM rate limited, retrying in {retry_delay:.0f}s")
            else:
                print(f"LLM error: {e}")
                traceback.print_exc()
            return False

    async def _run_loop(self):
        await asyncio.sleep(3)
        while True:
            self._urgent.clear()
            await self._try_generate()

            try:
                await asyncio.wait_for(self._urgent.wait(), timeout=self._interval)
            except asyncio.TimeoutError:
                pass

    async def _critical_monitor(self):
        await asyncio.sleep(5)
        while True:
            try:
                is_critical = _detect_critical_state()
                current_severity = (
                    self.latest_insight.get("severity") if self.latest_insight else None
                )
                if is_critical and current_severity != "critical":
                    self.trigger_urgent()
            except Exception:
                pass
            await asyncio.sleep(CRITICAL_MONITOR_INTERVAL)

    def start_background_task(self):
        if self._run_task is None:
            self._run_task = asyncio.create_task(self._run_loop())
            self._monitor_task = asyncio.create_task(self._critical_monitor())
            print(f"LLM insight service started (model={PathwayConfig.GEMINI_MODEL}, interval={self._interval}s)")

    async def stop_background_task(self):
        for task in (self._run_task, self._monitor_task):
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass


llm_insight_service = LLMInsightService()
