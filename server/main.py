from dotenv import load_dotenv
load_dotenv()

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.routes import router
from services.grid_context import grid_context_service
from services.devices import device_manager
from services.llm_insight import llm_insight_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    device_manager.start_background_task()
    grid_context_service.start_background_task()
    llm_insight_service.start_background_task()
    
    print("Data streams initialized:")
    print("- Internal stream: 4 devices (motor, HVAC, compressor, lighting) @ 10Hz")
    print("- External stream: Grid context (carbon, pricing) @ 15min intervals")
    print("- LLM insight service: Gemini analysis @ 30s intervals")
    
    yield
    
    await llm_insight_service.stop_background_task()
    await device_manager.stop_background_task()
    await grid_context_service.stop_background_task()
    print("All services stopped")


app = FastAPI(
    title="Grid Sense API",
    description="Real-time grid current monitoring and simulation API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)