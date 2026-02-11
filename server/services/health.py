class HealthService:
    def check_system_status(self):
        return {
            "status": "ok",
            "message": "System is running smoothly"
        }

health_service = HealthService()