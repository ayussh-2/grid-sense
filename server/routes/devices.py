from fastapi import APIRouter, HTTPException
from services.devices import device_manager

router = APIRouter()


@router.get("")
def list_devices():
    """
    List all available devices.
    Returns device IDs and types.
    """
    devices = device_manager.get_all_telemetry()
    return {
        "device_count": len(devices),
        "devices": [
            {
                "device_id": data["device_id"],
                "device_type": data["device_type"],
                "status": data["status"]
            }
            for data in devices.values()
        ]
    }


@router.get("/telemetry")
def get_all_device_telemetry():
    """
    Get telemetry from all devices.
    High-frequency internal stream data.
    """
    return device_manager.get_all_telemetry()


@router.get("/{device_id}")
def get_device_telemetry(device_id: str):
    """
    Get telemetry from a specific device.
    """
    telemetry = device_manager.get_device_telemetry(device_id)
    if "error" in telemetry:
        raise HTTPException(status_code=404, detail="Device not found")
    return telemetry


@router.post("/{device_id}/control/on")
def turn_device_on(device_id: str):
    """
    Turn on a device.
    """
    device = device_manager.get_device(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    device.turn_on()
    return {
        "status": "success",
        "message": f"Device {device_id} turned on",
        "device_status": device.status
    }


@router.post("/{device_id}/control/off")
def turn_device_off(device_id: str):
    """
    Turn off a device.
    """
    device = device_manager.get_device(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    device.turn_off()
    return {
        "status": "success",
        "message": f"Device {device_id} turned off",
        "device_status": device.status
    }


@router.post("/{device_id}/control/brightness")
def set_lighting_brightness(device_id: str, level: int):
    """
    Set brightness level for lighting devices (0-100).
    """
    device = device_manager.get_device(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    if device.device_type != "lighting":
        raise HTTPException(status_code=400, detail="Device is not a lighting system")
    
    if not 0 <= level <= 100:
        raise HTTPException(status_code=400, detail="Brightness level must be between 0 and 100")
    
    device.set_brightness(level)
    return {
        "status": "success",
        "message": f"Brightness set to {level}%",
        "brightness": device.brightness
    }


@router.post("/{device_id}/control/start")
def start_motor_device(device_id: str):
    """
    Start motor device (triggers inrush current).
    Only works for motor devices.
    """
    device = device_manager.get_device(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    if device.device_type != "motor":
        raise HTTPException(status_code=400, detail="Device is not a motor")
    
    return device.start()


@router.post("/{device_id}/control/inject-fault")
def inject_motor_fault(device_id: str):
    """
    Inject locked rotor fault into motor device.
    Only works for motor devices.
    """
    device = device_manager.get_device(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    if device.device_type != "motor":
        raise HTTPException(status_code=400, detail="Device is not a motor")
    
    return device.inject_fault()
