from fastapi import APIRouter
from services.health import health_service
router = APIRouter()

@router.get("/")
async def get_health():
    status_report = health_service.check_system_status()
    return status_report