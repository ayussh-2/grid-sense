"""
Pathway Utility Functions

Helper functions for stream processing, data fetching, and transformations.
"""

import requests
import time
import json
import os
from typing import Dict, Any, Generator
from .config import PathwayConfig


def fetch_internal_stream() -> Dict[str, Any]:
    """
    Fetch data from internal stream endpoint
    
    Returns:
        Dictionary containing device telemetry data
        
    Raises:
        requests.RequestException: If request fails
    """
    response = requests.get(
        PathwayConfig.get_internal_url(),
        timeout=PathwayConfig.REQUEST_TIMEOUT
    )
    response.raise_for_status()
    return response.json()


def fetch_external_stream() -> Dict[str, Any]:
    """
    Fetch data from external stream endpoint
    
    Returns:
        Dictionary containing grid context data
        
    Raises:
        requests.RequestException: If request fails
    """
    response = requests.get(
        PathwayConfig.get_external_url(),
        timeout=PathwayConfig.REQUEST_TIMEOUT
    )
    response.raise_for_status()
    return response.json()


def internal_stream_generator() -> Generator[Dict[str, Any], None, None]:
    """
    Generator function that yields device telemetry data
    
    Polls the internal stream endpoint at configured interval (10Hz default).
    Yields one record per device per poll.
    
    Yields:
        Dictionary with device telemetry fields:
        - device_id: str
        - device_type: str
        - status: str
        - voltage: float
        - current: float
        - power: float
        - timestamp: float
    """
    print(f"📡 Starting internal stream ({1/PathwayConfig.INTERNAL_POLL_INTERVAL:.0f}Hz)...")
    
    while True:
        try:
            data = fetch_internal_stream()
            timestamp = data.get('timestamp', time.time())
            
            for device_id, telemetry in data.get('devices', {}).items():
                yield {
                    'device_id': str(device_id),
                    'device_type': str(telemetry['device_type']),
                    'status': str(telemetry['status']),
                    'voltage': float(telemetry['voltage']),
                    'current': float(telemetry['current']),
                    'power': float(telemetry['power']),
                    'timestamp': float(timestamp)
                }
        except Exception as e:
            print(f"⚠️  Error in internal stream: {e}")
        
        time.sleep(PathwayConfig.INTERNAL_POLL_INTERVAL)


def external_stream_generator() -> Generator[Dict[str, Any], None, None]:
    """
    Generator function that yields grid context data
    
    Polls the external stream endpoint at configured interval (15s demo, 15min prod).
    Yields one record per poll.
    
    Yields:
        Dictionary with grid context fields:
        - carbon_intensity: float
        - carbon_level: str
        - electricity_price: float
        - pricing_tier: str
        - renewable_pct: float
        - timestamp: float
    """
    print(f"📡 Starting external stream ({PathwayConfig.EXTERNAL_POLL_INTERVAL:.0f}s updates)...")
    
    while True:
        try:
            data = fetch_external_stream()
            yield {
                'carbon_intensity': float(data['carbon_intensity']),
                'carbon_level': str(data['carbon_level']),
                'electricity_price': float(data['electricity_price']),
                'pricing_tier': str(data['pricing_tier']),
                'renewable_pct': float(data['grid_renewable_percentage']),
                'timestamp': float(data['last_updated'])
            }
        except Exception as e:
            print(f"⚠️  Error in external stream: {e}")
        
        time.sleep(PathwayConfig.EXTERNAL_POLL_INTERVAL)


def check_api_server() -> bool:
    """
    Check if the GridSense API server is running and accessible
    
    Returns:
        True if server is accessible, False otherwise
    """
    try:
        response = requests.get(
            f"{PathwayConfig.API_BASE_URL}/api/devices",
            timeout=PathwayConfig.REQUEST_TIMEOUT
        )
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def get_anomaly_alert(current: float, status: str) -> str:
    """
    Generate appropriate alert message based on current and status
    
    Args:
        current: Current in amperes
        status: Device status (off, starting, running, fault)
        
    Returns:
        Alert message string
    """
    if status == 'starting' and current > PathwayConfig.HIGH_CURRENT_THRESHOLD:
        return f"⚠️ MOTOR INRUSH: {current:.1f}A"
    elif status == 'fault':
        return f"🚨 FAULT DETECTED: {current:.1f}A"
    elif current > PathwayConfig.HIGH_CURRENT_THRESHOLD:
        return f"⚡ HIGH CURRENT: {current:.1f}A"
    else:
        return f"⚠️ ANOMALY: {current:.1f}A"


def get_recommendation(power: float, carbon_level: str, pricing_tier: str) -> str:
    """
    Generate optimization recommendation based on conditions
    
    Args:
        power: Power consumption in watts
        carbon_level: Carbon intensity level (LOW, MEDIUM, HIGH)
        pricing_tier: Pricing tier (LOW, MEDIUM, HIGH)
        
    Returns:
        Recommendation message string
    """
    if pricing_tier == 'HIGH' and carbon_level == 'HIGH':
        return "REDUCE LOAD - High Price & Carbon"
    elif pricing_tier == 'HIGH':
        return "PEAK DEMAND - Consider Reducing"
    elif pricing_tier == 'LOW' and carbon_level == 'LOW':
        return "OPTIMAL TIME - Low Cost & Carbon"
    else:
        return "NORMAL OPERATION"


def generate_llm_recommendation(
    device_id: str,
    device_type: str,
    status: str,
    power: float,
    current: float,
    carbon_intensity: float,
    carbon_level: str,
    electricity_price: float,
    pricing_tier: str,
    renewable_pct: float,
    cost_per_hour: float
) -> str:
    """
    Generate specific, actionable recommendation using rule-based logic.

    Prioritizes safety-critical conditions (fault, overcurrent) before
    cost/carbon optimization.
    """

    # Safety-critical: fault condition
    if status == 'fault':
        return (
            f"FAULT on {device_id} ({device_type}) drawing {current:.0f}A / {power:.0f}W. "
            f"Shut down immediately to prevent damage. Wasting ${cost_per_hour:.2f}/hr."
        )

    # Safety-critical: overcurrent during inrush
    if status == 'starting' and current > PathwayConfig.HIGH_CURRENT_THRESHOLD:
        return (
            f"{device_id} inrush at {current:.0f}A ({power:.0f}W). "
            f"Monitor closely -- will settle to steady-state in ~3s."
        )

    # Safety-critical: sustained overcurrent in running state
    if current > PathwayConfig.HIGH_CURRENT_THRESHOLD:
        return (
            f"{device_id} drawing {current:.0f}A (>{PathwayConfig.HIGH_CURRENT_THRESHOLD:.0f}A threshold). "
            f"Reduce load or shut down. Costing ${cost_per_hour:.2f}/hr."
        )

    # Cost optimization: high pricing
    if pricing_tier == 'HIGH' and power > 500:
        return (
            f"Grid price ${electricity_price:.3f}/kWh (High). "
            f"Stopping {device_id} saves ~${cost_per_hour:.2f}/hr."
        )

    if pricing_tier == 'HIGH' and carbon_level == 'HIGH':
        carbon_per_hour = (power / 1000) * carbon_intensity
        return (
            f"Peak pricing (${electricity_price:.3f}/kWh) + high carbon ({carbon_intensity:.0f}gCO2/kWh). "
            f"Reducing {device_id} saves ${cost_per_hour:.2f}/hr and {carbon_per_hour:.0f}g CO2/hr."
        )

    # Carbon optimization
    if carbon_level == 'HIGH' and power > 500:
        carbon_per_hour = (power / 1000) * carbon_intensity
        return (
            f"Carbon intensity {carbon_intensity:.0f}gCO2/kWh (High). "
            f"Deferring {device_id} avoids {carbon_per_hour:.0f}g CO2/hr."
        )

    # Optimal conditions
    if pricing_tier == 'LOW' and carbon_level == 'LOW':
        return (
            f"Optimal conditions: ${electricity_price:.3f}/kWh, {renewable_pct:.0f}% renewable. "
            f"Good time to run {device_id}."
        )

    if renewable_pct > 70:
        return (
            f"Grid is {renewable_pct:.0f}% renewable. "
            f"{device_id} running on mostly clean power."
        )

    # Normal operation
    return (
        f"{device_id} operating normally at {current:.1f}A. "
        f"Cost: ${cost_per_hour:.2f}/hr at ${electricity_price:.3f}/kWh."
    )


def create_llm_prompt(
    device_id: str,
    device_type: str,
    status: str,
    power: float,
    current: float,
    carbon_intensity: float,
    carbon_level: str,
    electricity_price: float,
    pricing_tier: str,
    renewable_pct: float,
    cost_per_hour: float
) -> str:
    """
    Create a detailed prompt for LLM-based recommendations.

    Returns:
        Formatted prompt string
    """
    return f"""You are an energy optimization assistant for an industrial facility. Generate a specific, actionable recommendation.

Context:
- Device: {device_id} ({device_type})
- Status: {status}
- Power Consumption: {power:.0f}W ({current:.1f}A)
- Current Cost: ${cost_per_hour:.2f}/hour
- Electricity Price: ${electricity_price:.3f}/kWh ({pricing_tier} pricing)
- Carbon Intensity: {carbon_intensity:.0f}gCO2/kWh ({carbon_level})
- Renewable Energy: {renewable_pct:.0f}%

Generate ONE concise recommendation (max 100 characters) that:
1. States the specific grid condition (price or carbon) or device fault
2. Gives a specific action with the device ID
3. Includes quantified savings ($ or CO2) or safety action

Example: "Grid Price is $0.27 (High). Stopping HVAC_001 will save approx $5/hour."

Recommendation:"""
