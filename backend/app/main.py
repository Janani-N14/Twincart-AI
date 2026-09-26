from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.core.logging import configure_logging
from app.routers import twins, campaigns, sellers, simulation, training

# Configure structured logging before anything else runs
configure_logging()

settings = get_settings()

app = FastAPI(
    title="TwinAI API",
    description=(
        "Hyperlocal Digital Twin & Agentic AI Platform for Bharat Commerce. "
        "Powered by LangGraph + Groq."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(twins.router, prefix="/api/twins", tags=["Digital Twins"])
app.include_router(campaigns.router, prefix="/api/campaigns", tags=["Campaigns"])
app.include_router(sellers.router, prefix="/api/sellers", tags=["Sellers"])
app.include_router(simulation.router, prefix="/api/simulation", tags=["Simulation"])
app.include_router(training.router, prefix="/api/training", tags=["ML Training & Image Generation"])


@app.get("/health", tags=["System"])
def health_check() -> dict[str, str]:
    """Liveness probe — returns 200 OK when the service is up."""
    return {"status": "ok", "env": settings.app_env}
