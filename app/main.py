
from fastapi import FastAPI

from app.routes.health import router as health_router

app = FastAPI(
    title="DataFlowEngine API",
    description="Data Processing and Workflow Automation",
    version="0.1.0"
)

app.include_router(
    health_router,
    prefix="/api",
    tags=["Health"]
)
