from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

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

# API Routers
app.include_router(twins.router, prefix="/api/twins", tags=["Digital Twins"])
app.include_router(campaigns.router, prefix="/api/campaigns", tags=["Campaigns"])
app.include_router(sellers.router, prefix="/api/sellers", tags=["Sellers"])
app.include_router(simulation.router, prefix="/api/simulation", tags=["Simulation"])
app.include_router(training.router, prefix="/api/training", tags=["ML Training & Image Generation"])


@app.get("/health", tags=["System"])
def health_check() -> dict[str, str]:
    """Liveness probe — returns 200 OK when the service is up."""
    return {"status": "ok", "env": settings.app_env}


# Static files & HTML Web Application UI
STATIC_DIR = Path(__file__).resolve().parent / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    @app.get("/", include_in_schema=False)
    def serve_ui():
        """Serve the single-page HTML5 UI dashboard."""
        return FileResponse(STATIC_DIR / "index.html")
