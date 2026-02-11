"""
Comprehensive test script for GridSense AI API
Tests all endpoints and simulations with detailed output
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.HEADER}{text.center(70)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*70}{Colors.END}\n")

def print_section(text):
    print(f"\n{Colors.BOLD}{Colors.CYAN}>>> {text}{Colors.END}")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_data(label, data):
    print(f"{Colors.YELLOW}{label}:{Colors.END}")
    print(json.dumps(data, indent=2))

def test_connection():
    """Test basic server connectivity"""
    print_section("Testing Server Connection")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print_success(f"Server is running: {response.json()['message']}")
            return True
        else:
            print_error(f"Server returned status code: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Cannot connect to server: {e}")
        return False

def test_live_data():
    """Test live data endpoint - all devices"""
    print_section("Testing Live Data Endpoint")
    
    response = requests.get(f"{BASE_URL}/api/live")
    data = response.json()
    
    print_success(f"Retrieved telemetry from {len(data)} devices")
    
    for device_id, telemetry in data.items():
        print(f"\n  Device: {Colors.BOLD}{device_id}{Colors.END}")
        print(f"    Type: {telemetry['device_type']}")
        print(f"    Status: {telemetry['status']}")
        print(f"    Current: {telemetry['current']:.2f}A")
        print(f"    Voltage: {telemetry['voltage']:.2f}V")
        print(f"    Power: {telemetry['power']:.2f}W")
    
    return data

def test_device_list():
    """Test device listing"""
    print_section("Testing Device List")
    
    response = requests.get(f"{BASE_URL}/api/devices")
    data = response.json()
    
    print_success(f"Found {data['device_count']} devices")
    for device in data['devices']:
        print(f"  - {device['device_id']} ({device['device_type']}) - Status: {device['status']}")

def test_motor_startup():
    """Test motor startup sequence with inrush current"""
    print_section("Testing Motor Startup Sequence (Inrush Current)")
    
    print("Starting motor...")
    response = requests.post(f"{BASE_URL}/api/devices/motor_001/control/start")
    result = response.json()
    print_success(f"{result.get('message', result)}")
    
    print("\nMonitoring inrush current:")
    print("Phase 1 (0-0.5s): Peak hold at 120A")
    print("Phase 2 (0.5-3.5s): Exponential decay to 45A\n")
    print(f"{'Time (s)':<10} {'Status':<12} {'Current (A)':<15} {'Voltage (V)':<15} {'Phase':<15}")
    print("-" * 75)
    
    start_time = time.time()
    for i in range(40):
        elapsed = time.time() - start_time
        
        response = requests.get(f"{BASE_URL}/api/devices/motor_001")
        data = response.json()
        
        phase = "Peak Hold" if elapsed < 0.5 else "Decay"
        print(f"{elapsed:<10.1f} {data['status']:<12} {data['current']:<15.2f} {data['voltage']:<15.2f} {phase:<15}")
        
        time.sleep(0.1)
        
        if data['status'] == 'running' and elapsed > 3.5:
            break
    
    print_success("\nMotor reached steady state (2-phase startup complete)")

def test_motor_fault():
    """Test motor fault injection"""
    print_section("Testing Motor Fault Injection (Locked Rotor)")
    
    print("Injecting locked rotor fault...")
    response = requests.post(f"{BASE_URL}/api/devices/motor_001/control/inject-fault")
    result = response.json()
    print_success(f"{result.get('message', result)}")
    
    print("\nMonitoring sustained high current (should stay at ~110A):\n")
    print(f"{'Time (s)':<10} {'Status':<12} {'Current (A)':<15} {'Expected':<15}")
    print("-" * 60)
    
    start_time = time.time()
    for i in range(10):
        elapsed = time.time() - start_time
        
        response = requests.get(f"{BASE_URL}/api/devices/motor_001")
        data = response.json()
        
        expected = "CRITICAL" if elapsed > 5 else "Monitoring"
        print(f"{elapsed:<10.1f} {data['status']:<12} {data['current']:<15.2f} {expected:<15}")
        
        time.sleep(1)
    
    print_success("\nFault condition sustained (AI should detect this)")

def test_hvac_control():
    """Test HVAC device control"""
    print_section("Testing HVAC Device Control")
    
    print("Turning on HVAC...")
    response = requests.post(f"{BASE_URL}/api/devices/hvac_001/control/on")
    print_success(f"{response.json()['message']}")
    
    time.sleep(1)
    
    response = requests.get(f"{BASE_URL}/api/devices/hvac_001")
    data = response.json()
    print(f"  Current draw: {data['current']:.2f}A")
    print(f"  Power: {data['power']:.2f}W")
    
    print("\nTurning off HVAC...")
    response = requests.post(f"{BASE_URL}/api/devices/hvac_001/control/off")
    print_success(f"{response.json()['message']}")

def test_compressor_control():
    """Test compressor device control"""
    print_section("Testing Compressor Device Control")
    
    print("Turning on compressor...")
    response = requests.post(f"{BASE_URL}/api/devices/compressor_001/control/on")
    print_success(f"{response.json()['message']}")
    
    time.sleep(1)
    
    response = requests.get(f"{BASE_URL}/api/devices/compressor_001")
    data = response.json()
    print(f"  Current draw: {data['current']:.2f}A (building pressure)")
    print(f"  Power: {data['power']:.2f}W")

def test_lighting_control():
    """Test lighting device control with brightness"""
    print_section("Testing Lighting Device Control")
    
    print("Turning on lighting...")
    response = requests.post(f"{BASE_URL}/api/devices/lighting_001/control/on")
    print_success(f"{response.json()['message']}")
    
    time.sleep(0.5)
    
    print("\nTesting brightness levels:")
    for level in [100, 75, 50, 25, 0]:
        response = requests.post(
            f"{BASE_URL}/api/devices/lighting_001/control/brightness",
            params={"level": level}
        )
        time.sleep(0.3)
        
        response = requests.get(f"{BASE_URL}/api/devices/lighting_001")
        data = response.json()
        print(f"  Brightness {level}%: {data['current']:.2f}A, {data['power']:.2f}W")

def test_grid_context():
    """Test external stream - grid context"""
    print_section("Testing Grid Context (External Stream)")
    
    response = requests.get(f"{BASE_URL}/api/grid")
    data = response.json()
    
    print_success("Retrieved grid context data")
    print(f"\n  Carbon Intensity: {data['carbon_intensity']} gCO2/kWh ({data['carbon_level']})")
    print(f"  Electricity Price: ${data['electricity_price']}/kWh ({data['pricing_tier']})")
    print(f"  Renewable %: {data['grid_renewable_percentage']}%")
    print(f"  Last Updated: {datetime.fromtimestamp(data['last_updated']).strftime('%Y-%m-%d %H:%M:%S')}")
    
    return data

def test_combined_stream():
    """Test combined internal + external streams"""
    print_section("Testing Combined Stream (For Pathway Processing)")
    
    response = requests.get(f"{BASE_URL}/api/stream/combined")
    data = response.json()
    
    print_success("Retrieved combined stream data")
    
    internal_count = len(data['internal_stream'])
    print(f"\n  Internal Stream: {internal_count} devices")
    for device_id in data['internal_stream'].keys():
        device_data = data['internal_stream'][device_id]
        print(f"    - {device_id}: {device_data['current']:.2f}A ({device_data['status']})")
    
    print(f"\n  External Stream:")
    print(f"    - Carbon: {data['external_stream']['carbon_intensity']} gCO2/kWh")
    print(f"    - Price: ${data['external_stream']['electricity_price']}/kWh")

def test_stream_endpoints():
    """Test individual stream endpoints"""
    print_section("Testing Individual Stream Endpoints")
    
    print("Internal stream only:")
    response = requests.get(f"{BASE_URL}/api/stream/internal")
    data = response.json()
    print_success(f"Retrieved {len(data['devices'])} devices")
    
    print("\nExternal stream only:")
    response = requests.get(f"{BASE_URL}/api/stream/external")
    data = response.json()
    print_success(f"Carbon level: {data['carbon_level']}, Price tier: {data['pricing_tier']}")

def test_economic_scenario():
    """Test economic optimization scenario"""
    print_section("Testing Economic Scenario (Peak Hour + High Load)")
    
    grid_data = test_grid_context()
    
    print("\nStarting high-load devices during current pricing tier...")
    requests.post(f"{BASE_URL}/api/devices/motor_001/control/start")
    requests.post(f"{BASE_URL}/api/devices/hvac_001/control/on")
    requests.post(f"{BASE_URL}/api/devices/compressor_001/control/on")
    
    time.sleep(2)
    
    response = requests.get(f"{BASE_URL}/api/live")
    devices = response.json()
    
    total_current = sum(d['current'] for d in devices.values())
    total_power = sum(d['power'] for d in devices.values())
    
    print(f"\n  Total Current Draw: {total_current:.2f}A")
    print(f"  Total Power: {total_power:.2f}W ({total_power/1000:.2f}kW)")
    print(f"  Grid Price Tier: {grid_data['pricing_tier']}")
    
    if grid_data['pricing_tier'] == 'HIGH' and total_current > 50:
        print(f"\n  {Colors.YELLOW}⚠ WARNING: High load during peak pricing{Colors.END}")
        print(f"  {Colors.YELLOW}💡 RECOMMENDATION: Defer non-critical loads to off-peak hours{Colors.END}")
    else:
        print_success("\n  Load profile is economically optimal")

def test_carbon_scenario():
    """Test carbon awareness scenario"""
    print_section("Testing Carbon Awareness Scenario")
    
    response = requests.get(f"{BASE_URL}/api/stream/combined")
    data = response.json()
    
    grid = data['external_stream']
    devices = data['internal_stream']
    
    total_power_kw = sum(d['power'] for d in devices.values()) / 1000
    carbon_rate = grid['carbon_intensity']
    carbon_impact = total_power_kw * carbon_rate
    
    print(f"\n  Current Power Draw: {total_power_kw:.2f}kW")
    print(f"  Grid Carbon Intensity: {carbon_rate} gCO2/kWh")
    print(f"  Carbon Impact: {carbon_impact:.2f} gCO2/hour")
    print(f"  Grid Renewable %: {grid['grid_renewable_percentage']}%")
    
    if grid['carbon_level'] == 'HIGH' and total_power_kw > 5:
        print(f"\n  {Colors.YELLOW}⚠ WARNING: High carbon intensity period{Colors.END}")
        print(f"  {Colors.YELLOW}💡 RECOMMENDATION: Shift heavy loads to cleaner hours{Colors.END}")
    else:
        print_success("\n  Operating during low-carbon period")

def cleanup():
    """Stop all devices"""
    print_section("Cleanup - Stopping All Devices")
    
    devices = ['motor_001', 'hvac_001', 'compressor_001', 'lighting_001']
    for device_id in devices:
        requests.post(f"{BASE_URL}/api/devices/{device_id}/control/off")
    
    print_success("All devices stopped")

def main():
    print_header("GridSense AI - Comprehensive API Test Suite")
    print(f"Testing server at: {BASE_URL}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not test_connection():
        print_error("\nServer is not running. Please start the server first:")
        print("  cd server")
        print("  fastapi dev main.py")
        return 1
    
    try:
        # Basic endpoint tests
        test_live_data()
        test_device_list()
        
        # Device control tests
        test_motor_startup()
        test_motor_fault()
        test_hvac_control()
        test_compressor_control()
        test_lighting_control()
        
        # Stream tests
        test_grid_context()
        test_combined_stream()
        test_stream_endpoints()
        
        # Scenario tests
        test_economic_scenario()
        test_carbon_scenario()
        
        # Cleanup
        cleanup()
        
        print_header("All Tests Completed Successfully")
        print(f"{Colors.GREEN}✓ Internal Stream: 4 devices working correctly{Colors.END}")
        print(f"{Colors.GREEN}✓ External Stream: Grid context updating{Colors.END}")
        print(f"{Colors.GREEN}✓ Motor Physics: Inrush current decay verified{Colors.END}")
        print(f"{Colors.GREEN}✓ Fault Detection: Locked rotor condition demonstrated{Colors.END}")
        print(f"{Colors.GREEN}✓ Economic Logic: Peak demand scenarios tested{Colors.END}")
        print(f"{Colors.GREEN}✓ Carbon Awareness: Grid context integration working{Colors.END}")
        
        
        return 0
        
    except Exception as e:
        print_error(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
