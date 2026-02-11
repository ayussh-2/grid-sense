import asyncio
import random
import time
from datetime import datetime
from typing import Literal

PricingTier = Literal["LOW", "MEDIUM", "HIGH"]
CarbonIntensity = Literal["LOW", "MEDIUM", "HIGH"]


class GridContextService:
    """
    Simulates external grid context data (low-frequency updates)
    
    This represents data from external APIs:
    - Carbon Intensity (gCO2/kWh)
    - Electricity Pricing ($/kWh)
    - Grid Status
    
    Updates every 15-60 minutes (configurable)
    """
    
    def __init__(self):
        self.context = {
            "carbon_intensity": 0.0,  # gCO2/kWh
            "carbon_level": "MEDIUM",  # LOW, MEDIUM, HIGH
            "electricity_price": 0.0,  # $/kWh
            "pricing_tier": "MEDIUM",  # LOW, MEDIUM, HIGH
            "grid_renewable_percentage": 0.0,  # 0-100%
            "last_updated": time.time(),
            "next_update_in": 0
        }
        self._task = None
        self.update_interval = 900  # 15 minutes in seconds (configurable)
    
    def _get_time_based_context(self) -> dict:
        """
        Generate context based on time of day
        
        Simulates real-world patterns:
        - High carbon during evening (7-10 PM) when coal/gas peak
        - Low carbon during day (10 AM - 3 PM) when solar is strong
        - High prices during peak hours (5-9 PM)
        - Low prices during off-peak (11 PM - 6 AM)
        """
        current_hour = datetime.now().hour
        
        # Carbon Intensity Pattern (gCO2/kWh)
        if 10 <= current_hour <= 15:
            # Daytime: Solar energy abundant
            carbon = random.uniform(200, 350)
            carbon_level = "LOW"
            renewable_pct = random.uniform(50, 70)
        elif 19 <= current_hour <= 22:
            # Evening peak: Coal/gas plants running
            carbon = random.uniform(600, 800)
            carbon_level = "HIGH"
            renewable_pct = random.uniform(10, 25)
        else:
            # Other times: Mixed generation
            carbon = random.uniform(400, 550)
            carbon_level = "MEDIUM"
            renewable_pct = random.uniform(30, 45)
        
        # Electricity Pricing Pattern ($/kWh)
        if 17 <= current_hour <= 21:
            # Peak hours: High demand, high price
            price = random.uniform(0.25, 0.35)
            pricing_tier = "HIGH"
        elif 23 <= current_hour or current_hour <= 6:
            # Off-peak: Low demand, low price
            price = random.uniform(0.08, 0.12)
            pricing_tier = "LOW"
        else:
            # Mid-peak
            price = random.uniform(0.15, 0.22)
            pricing_tier = "MEDIUM"
        
        return {
            "carbon_intensity": round(carbon, 2),
            "carbon_level": carbon_level,
            "electricity_price": round(price, 4),
            "pricing_tier": pricing_tier,
            "grid_renewable_percentage": round(renewable_pct, 2)
        }
    
    def get_context(self) -> dict:
        """Get current grid context"""
        return self.context.copy()
    
    async def run_simulation(self):
        """
        Background task that updates grid context periodically
        Updates every 15 minutes (900 seconds) by default
        """
        while True:
            # Generate new context based on time of day
            new_context = self._get_time_based_context()
            
            # Update state
            self.context.update(new_context)
            self.context["last_updated"] = time.time()
            self.context["next_update_in"] = self.update_interval
            
            # Wait for next update
            await asyncio.sleep(self.update_interval)
    
    def start_background_task(self):
        """Start the background update task"""
        if self._task is None:
            self._task = asyncio.create_task(self.run_simulation())
            print("Grid context service initialized")
    
    async def stop_background_task(self):
        """Stop the background update task"""
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            print("Grid context service stopped")


grid_context_service = GridContextService()
