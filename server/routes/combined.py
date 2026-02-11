from fastapi import APIRouter
from services.grid_context import grid_context_service
from services.devices import device_manager

router = APIRouter()


@router.get("/combined")
def get_combined_stream():
    """
    Combined data from both internal and external streams for Pathway processing.
    
    Internal Stream (High-Frequency @ 10Hz):
    - Motor: Industrial induction motor with physics-based states
    - HVAC: Temperature-controlled climate system
    - Compressor: Pressure-based air compressor
    - Lighting: Brightness-controlled lighting system
    
    External Stream (Low-Frequency @ 15min):
    - Carbon intensity: gCO2/kWh (time-of-day based)
    - Electricity pricing: $/kWh (peak/off-peak tiers)
    - Renewable percentage: Grid renewable energy mix
    
    This endpoint provides the complete data context for:
    - Real-time anomaly detection (Safety Gate)
    - Economic optimization (Peak demand management)
    - Carbon-aware load shifting (Sustainability Gate)
    
    Response structure:
    {
      "internal_stream": {
        "motor_001": {...},
        "hvac_001": {...},
        "compressor_001": {...},
        "lighting_001": {...}
      },
      "external_stream": {
        "carbon_intensity": 425.5,
        "carbon_level": "MEDIUM",
        "electricity_price": 0.18,
        "pricing_tier": "MEDIUM",
        "grid_renewable_percentage": 38.5,
        ...
      },
      "timestamp": 1708563245.123
    }
    """
    devices_data = device_manager.get_all_telemetry()
    grid_data = grid_context_service.get_context()
    
    # Get timestamp from first device
    timestamp = next(iter(devices_data.values()))["timestamp"] if devices_data else 0
    
    return {
        "internal_stream": devices_data,
        "external_stream": grid_data,
        "timestamp": timestamp
    }


@router.get("/internal")
def get_internal_stream():
    """
    Internal stream only: All device telemetry data.
    
    High-frequency data sampled at 10Hz (100ms intervals).
    Includes motor, HVAC, compressor, and lighting systems.
    
    Use this endpoint when you only need device data without grid context.
    """
    devices_data = device_manager.get_all_telemetry()
    timestamp = next(iter(devices_data.values()))["timestamp"] if devices_data else 0
    
    return {
        "devices": devices_data,
        "timestamp": timestamp
    }


@router.get("/external")
def get_external_stream():
    """
    External stream only: Grid context data.
    
    Low-frequency data updated every 15 minutes.
    Includes carbon intensity, electricity pricing, and renewable percentage.
    
    Use this endpoint when you only need grid context without device telemetry.
    """
    return grid_context_service.get_context()
