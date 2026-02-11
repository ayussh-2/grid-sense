from fastapi import APIRouter
from services.grid_context import grid_context_service

router = APIRouter()


@router.get("")
def get_grid_context():
    """
    Get current grid context (external stream).
    
    This endpoint provides low-frequency data from external sources:
    - Carbon intensity (gCO2/kWh)
    - Electricity pricing ($/kWh)
    - Renewable energy percentage
    
    Updates every 15 minutes.
    """
    return grid_context_service.get_context()
