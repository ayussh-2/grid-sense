from fastapi import APIRouter
from services.devices import device_manager

router = APIRouter()


@router.get("")
def get_live_data():
    """
    Get real-time telemetry data from all devices.
    
    Returns comprehensive telemetry for all connected devices:
    - Motor: Industrial induction motor with physics-based simulation
    - HVAC: Climate control system
    - Compressor: Industrial air compressor
    - Lighting: Lighting system with brightness control
    
    Each device provides:
    - device_id: Unique identifier
    - device_type: Type of device (motor, hvac, compressor, lighting)
    - status: Current state (off, starting, running, fault)
    - voltage: Line voltage in Volts
    - current: Current draw in Amperes
    - power: Power consumption in Watts
    - timestamp: Unix timestamp of measurement
    
    Poll this endpoint at 1Hz (every second) for dashboard updates.
    Internal data stream updates at 10Hz (100ms intervals).
    """
    return device_manager.get_all_telemetry()
