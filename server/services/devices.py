import asyncio
import math
import random
import time
from typing import Literal

DeviceType = Literal["motor", "hvac", "compressor", "lighting"]
DeviceStatus = Literal["off", "starting", "running", "fault"]


class Device:
    """Base class for all device simulators"""
    
    def __init__(self, device_id: str, device_type: DeviceType):
        self.device_id = device_id
        self.device_type = device_type
        self.status = "off"
        self.voltage = 230.0
        self.current = 0.0
        self.power = 0.0
        self.timestamp = time.time()
    
    def get_telemetry(self) -> dict:
        """Get current telemetry for this device"""
        return {
            "device_id": self.device_id,
            "device_type": self.device_type,
            "status": self.status,
            "voltage": self.voltage,
            "current": self.current,
            "power": self.power,
            "timestamp": self.timestamp
        }
    
    def update(self):
        """Update device telemetry - override in subclasses"""
        raise NotImplementedError


class MotorDevice(Device):
    """
    Industrial induction motor with physics-based simulation.
    
    States:
    - off: Motor idle (0A)
    - starting: Inrush current with peak hold then decay
      * 0-0.5s: Hold at 120A (peak inrush)
      * 0.5-3.5s: Exponential decay to 45A
    - running: Normal operation (40-45A with Gaussian noise)
    - fault: Locked rotor condition (110A sustained)
    """
    
    def __init__(self, device_id: str):
        super().__init__(device_id, "motor")
        self.startup_elapsed = 0.0
        self.inrush_peak = 120.0
        self.steady_nominal = 42.5
        self.locked_rotor_current = 110.0
        self.startup_duration = 3.5
        self.peak_hold_duration = 0.5  # Hold at peak for 0.5s before decay
        self.time_constant = 0.8
    
    def update(self):
        self.timestamp = time.time()
        self.voltage = 230.0 if self.status != "off" else 0.0
        
        if self.status == "off":
            self.current = 0.0
            self.voltage = 0.0
            self.power = 0.0
            
        elif self.status == "starting":
            # Two-phase startup: hold peak, then exponential decay
            t = self.startup_elapsed
            
            if t < self.peak_hold_duration:
                # Phase 1: Hold at peak inrush current (0-0.5s)
                self.current = round(self.inrush_peak + random.uniform(-0.5, 0.5), 2)
            else:
                # Phase 2: Exponential decay (0.5s onwards)
                # Adjust time for decay calculation
                decay_time = t - self.peak_hold_duration
                tau = self.time_constant
                decay = self.inrush_peak * math.exp(-decay_time / tau)
                self.current = round(decay + self.steady_nominal, 2)
                
                # Clamp to steady state
                if self.current <= 45:
                    self.current = self.steady_nominal
            
            self.voltage = 230.0 + random.gauss(0, 2)
            self.power = round(self.voltage * self.current, 2)
            
            # Auto-transition to running after total startup duration
            self.startup_elapsed += 0.1
            if self.startup_elapsed >= self.startup_duration:
                self.status = "running"
                self.startup_elapsed = 0.0
                
        elif self.status == "running":
            # Normal operation with Gaussian noise
            self.current = random.gauss(self.steady_nominal, 1.0)
            self.current = max(40.0, min(45.0, self.current))
            self.current = round(self.current, 2)
            self.voltage = 230.0 + random.gauss(0, 2)
            self.power = round(self.voltage * self.current, 2)
            
        elif self.status == "fault":
            # Locked rotor: sustained high current
            self.current = round(self.locked_rotor_current + random.uniform(-0.5, 0.5), 2)
            self.voltage = 230.0 + random.gauss(0, 2)
            self.power = round(self.voltage * self.current, 2)
    
    def start(self):
        """Start the motor"""
        if self.status == "off":
            self.status = "starting"
            self.startup_elapsed = 0.0
            return {
                "status": "success", 
                "message": "Motor starting - peak inrush 120A for 0.5s, then decay to 45A"
            }
        return {"status": "error", "message": f"Cannot start from {self.status} state"}
    
    def turn_on(self):
        """Alias for start() to match Device interface"""
        return self.start()
    
    def turn_off(self):
        """Stop the motor"""
        self.status = "off"
        self.startup_elapsed = 0.0
        return {"status": "success", "message": "Motor stopped"}
    
    def inject_fault(self):
        """Inject locked rotor fault"""
        previous = self.status
        self.status = "fault"
        return {
            "status": "success", 
            "message": "Locked rotor fault injected",
            "previous_status": previous
        }


class HVACDevice(Device):
    """HVAC system simulator"""
    
    def __init__(self, device_id: str):
        super().__init__(device_id, "hvac")
        self.target_temp = 22.0
        self.current_temp = 25.0
        self.compressor_speed = 0  # 0-100%
    
    def update(self):
        self.timestamp = time.time()
        
        if self.status == "off":
            self.current = 0.0
            self.power = 0.0
        elif self.status == "running":
            # HVAC current varies with compressor speed
            # Base: 5A standby + variable load
            temp_diff = abs(self.current_temp - self.target_temp)
            self.compressor_speed = min(100, temp_diff * 20)
            
            self.current = 5.0 + (self.compressor_speed / 100) * 15.0  # 5-20A
            self.current += random.gauss(0, 0.3)  # Noise
            self.voltage = 230.0 + random.gauss(0, 2)
            self.power = self.voltage * self.current
            
            # Temperature gradually approaches target
            if self.current_temp > self.target_temp:
                self.current_temp -= 0.1
            elif self.current_temp < self.target_temp:
                self.current_temp += 0.1
    
    def turn_on(self):
        self.status = "running"
    
    def turn_off(self):
        self.status = "off"
        self.compressor_speed = 0


class CompressorDevice(Device):
    """Industrial air compressor simulator"""
    
    def __init__(self, device_id: str):
        super().__init__(device_id, "compressor")
        self.pressure = 0.0  # PSI
        self.target_pressure = 120.0
    
    def update(self):
        self.timestamp = time.time()
        
        if self.status == "off":
            self.current = 0.0
            self.power = 0.0
            self.pressure = max(0, self.pressure - 1)  # Pressure leaks
        elif self.status == "running":
            # Compressor draws high current when building pressure
            if self.pressure < self.target_pressure:
                self.current = random.uniform(25, 30)  # Building pressure
                self.pressure += 2
            else:
                self.current = random.uniform(5, 8)  # Maintaining pressure
                self.pressure += random.uniform(-0.5, 0.5)
            
            self.voltage = 230.0 + random.gauss(0, 2)
            self.power = self.voltage * self.current
    
    def turn_on(self):
        self.status = "running"
    
    def turn_off(self):
        self.status = "off"


class LightingDevice(Device):
    """Lighting system simulator"""
    
    def __init__(self, device_id: str):
        super().__init__(device_id, "lighting")
        self.brightness = 100  # 0-100%
    
    def update(self):
        self.timestamp = time.time()
        
        if self.status == "off":
            self.current = 0.0
            self.power = 0.0
        elif self.status == "running":
            # Lighting current proportional to brightness
            self.current = (self.brightness / 100) * 2.5  # Max 2.5A at 100%
            self.current += random.gauss(0, 0.05)  # Small noise
            self.voltage = 230.0 + random.gauss(0, 1)
            self.power = self.voltage * self.current
    
    def turn_on(self):
        self.status = "running"
    
    def turn_off(self):
        self.status = "off"
    
    def set_brightness(self, level: int):
        """Set brightness level (0-100)"""
        self.brightness = max(0, min(100, level))


class DeviceManager:
    """
    Manages multiple device simulators
    Provides centralized access to all device telemetry
    """
    
    def __init__(self):
        self.devices = {}
        self._task = None
        
        # Initialize default devices
        self.add_device(MotorDevice("motor_001"))
        self.add_device(HVACDevice("hvac_001"))
        self.add_device(CompressorDevice("compressor_001"))
        self.add_device(LightingDevice("lighting_001"))
    
    def add_device(self, device: Device):
        """Add a device to the manager"""
        self.devices[device.device_id] = device
    
    def get_device(self, device_id: str) -> Device:
        """Get a specific device"""
        return self.devices.get(device_id)
    
    def get_all_telemetry(self) -> dict:
        """Get telemetry from all devices"""
        return {
            device_id: device.get_telemetry()
            for device_id, device in self.devices.items()
        }
    
    def get_device_telemetry(self, device_id: str) -> dict:
        """Get telemetry from a specific device"""
        device = self.devices.get(device_id)
        if device:
            return device.get_telemetry()
        return {"error": "Device not found"}
    
    async def run_simulation(self):
        """Background task that updates all devices"""
        while True:
            for device in self.devices.values():
                device.update()
            await asyncio.sleep(0.1)  # 10Hz update rate
    
    def start_background_task(self):
        """Start the device simulation loop"""
        if self._task is None:
            self._task = asyncio.create_task(self.run_simulation())
            print(f"Device manager initialized with {len(self.devices)} devices")
    
    async def stop_background_task(self):
        """Stop the device simulation loop"""
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            print("Device manager stopped")


device_manager = DeviceManager()
