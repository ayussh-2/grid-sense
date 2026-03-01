import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.devices import device_manager
from services.grid_context import grid_context_service
from services.llm_insight import llm_insight_service
from routes.pathway_routes import read_latest_jsonl
from pathlib import Path

router = APIRouter()

PATHWAY_OUTPUT_DIR = Path("pathway_output")

LIVE_DATA_INTERVAL = 1.0
GRID_CONTEXT_INTERVAL = 60.0
PATHWAY_INTERVAL = 2.0
LLM_INSIGHT_POLL = 1.0


async def push_live_data(ws: WebSocket, stop: asyncio.Event):
    while not stop.is_set():
        try:
            telemetry = device_manager.get_all_telemetry()
            await ws.send_json({"type": "live_data", "data": telemetry})
        except (WebSocketDisconnect, RuntimeError):
            break
        await asyncio.sleep(LIVE_DATA_INTERVAL)


async def push_grid_context(ws: WebSocket, stop: asyncio.Event):
    while not stop.is_set():
        try:
            ctx = grid_context_service.get_context()
            await ws.send_json({"type": "grid_context", "data": ctx})
        except (WebSocketDisconnect, RuntimeError):
            break
        await asyncio.sleep(GRID_CONTEXT_INTERVAL)


async def push_pathway_data(ws: WebSocket, stop: asyncio.Event):
    while not stop.is_set():
        try:
            anomalies_file = PATHWAY_OUTPUT_DIR / "anomalies.jsonl"
            stats_file = PATHWAY_OUTPUT_DIR / "device_stats.jsonl"
            recommendations_file = PATHWAY_OUTPUT_DIR / "recommendations.jsonl"

            is_active = any(
                (PATHWAY_OUTPUT_DIR / f).exists()
                for f in ["anomalies.jsonl", "device_stats.jsonl", "recommendations.jsonl", "total_power.jsonl"]
            )

            payload = {"pathway_active": is_active}

            if is_active:
                anomalies = read_latest_jsonl(anomalies_file, max_lines=20)
                recommendations = read_latest_jsonl(recommendations_file, max_lines=20)

                stats_raw = read_latest_jsonl(stats_file, max_lines=100)
                latest_stats = {}
                for entry in stats_raw:
                    device_type = entry.get("device_type")
                    if device_type:
                        latest_stats[device_type] = entry

                payload["anomalies"] = anomalies
                payload["recommendations"] = recommendations
                payload["statistics"] = latest_stats

            await ws.send_json({"type": "pathway_data", "data": payload})
        except (WebSocketDisconnect, RuntimeError):
            break
        await asyncio.sleep(PATHWAY_INTERVAL)


async def push_llm_insight(ws: WebSocket, stop: asyncio.Event):
    """Push LLM insight as soon as a new version is available."""
    last_version = 0
    while not stop.is_set():
        try:
            if llm_insight_service.version != last_version:
                insight = llm_insight_service.latest_insight
                if insight:
                    await ws.send_json({"type": "llm_insight", "data": insight})
                    last_version = llm_insight_service.version
        except (WebSocketDisconnect, RuntimeError):
            break
        await asyncio.sleep(LLM_INSIGHT_POLL)


@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    stop = asyncio.Event()

    tasks = [
        asyncio.create_task(push_live_data(ws, stop)),
        asyncio.create_task(push_grid_context(ws, stop)),
        asyncio.create_task(push_pathway_data(ws, stop)),
        asyncio.create_task(push_llm_insight(ws, stop)),
    ]

    try:
        while True:
            data = await ws.receive_text()
            if data == "ping":
                await ws.send_json({"type": "pong"})
    except WebSocketDisconnect:
        pass
    finally:
        stop.set()
        for t in tasks:
            t.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
