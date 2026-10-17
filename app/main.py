
from fastapi import FastAPI

from app.routes.health import router as health_router
from app.routes.files import router as files_router


app = FastAPI(
    title="DataFlowEngine API",
    description="Data Processing and Workflow Automation",
    version="0.4.0"
)

app.include_router(
    health_router,
    prefix="/api",
    tags=["Health"]
)

app.include_router(
    files_router,
    prefix="/api",
    tags=["Excel"]
)
