from fastapi import APIRouter
from services.devices import device_manager
from services.llm_insight import llm_insight_service

router = APIRouter()

SCENARIOS = {
    "surge": {
        "name": "Surge All Devices",
        "description": "Turn on all devices and inject motor fault. Triggers anomaly detection, critical alerts, and LLM cost-saving recommendations.",
        "showcases": ["Pathway anomaly detection", "Fault alerts", "LLM recommendations", "Critical status"],
    },
    "motor_inrush": {
        "name": "Motor Inrush",
        "description": "Start motor from off. Shows 120A peak inrush for 0.5s decaying to 45A steady-state.",
        "showcases": ["Transient spike detection", "Inrush current profiling", "Real-time chart spike"],
    },
    "high_load": {
        "name": "High Load",
        "description": "Run motor, HVAC, and compressor together (~90A). Triggers warning-level status and optimization tips.",
        "showcases": ["Warning status", "LLM cost optimization", "Device statistics"],
    },
    "normal": {
        "name": "Normal Operation",
        "description": "Run HVAC and lighting at stable levels (~22A). Shows green status and optimal-condition recommendations.",
        "showcases": ["Normal status", "Optimal grid recommendations", "Steady baselines"],
    },
    "fault": {
        "name": "Inject Fault",
        "description": "Inject locked rotor fault on motor (110A sustained). Triggers fault anomaly and critical alerts.",
        "showcases": ["Fault detection", "Anomaly alerts", "Critical status"],
    },
    "reset": {
        "name": "Reset",
        "description": "Turn off all devices. Returns system to idle baseline.",
        "showcases": ["Normal status", "Zero baseline"],
    },
}


def _apply_surge():
    motor = device_manager.get_device("motor_001")
    hvac = device_manager.get_device("hvac_001")
    compressor = device_manager.get_device("compressor_001")
    lighting = device_manager.get_device("lighting_001")
    motor.turn_on()
    hvac.turn_on()
    compressor.turn_on()
    lighting.turn_on()
    motor.inject_fault()
    llm_insight_service.trigger_urgent()


def _apply_motor_inrush():
    motor = device_manager.get_device("motor_001")
    motor.turn_off()
    motor.start()


def _apply_high_load():
    motor = device_manager.get_device("motor_001")
    hvac = device_manager.get_device("hvac_001")
    compressor = device_manager.get_device("compressor_001")
    lighting = device_manager.get_device("lighting_001")
    lighting.turn_off()
    if motor.status == "off":
        motor.start()
    hvac.turn_on()
    compressor.turn_on()


def _apply_normal():
    motor = device_manager.get_device("motor_001")
    compressor = device_manager.get_device("compressor_001")
    hvac = device_manager.get_device("hvac_001")
    lighting = device_manager.get_device("lighting_001")
    motor.turn_off()
    compressor.turn_off()
    hvac.turn_on()
    lighting.turn_on()


def _apply_fault():
    motor = device_manager.get_device("motor_001")
    if motor.status == "off":
        motor.start()
    motor.inject_fault()
    llm_insight_service.trigger_urgent()


def _apply_reset():
    for device in device_manager.devices.values():
        device.turn_off()


_SCENARIO_FNS = {
    "surge": _apply_surge,
    "motor_inrush": _apply_motor_inrush,
    "high_load": _apply_high_load,
    "normal": _apply_normal,
    "fault": _apply_fault,
    "reset": _apply_reset,
}


@router.get("/scenarios")
def list_scenarios():
    return {"scenarios": SCENARIOS}


@router.post("/scenarios/{scenario_id}")
def run_scenario(scenario_id: str):
    if scenario_id not in SCENARIOS:
        return {"status": "error", "message": f"Unknown scenario: {scenario_id}"}

    _SCENARIO_FNS[scenario_id]()

    return {
        "status": "success",
        "scenario": scenario_id,
        **SCENARIOS[scenario_id],
    }
