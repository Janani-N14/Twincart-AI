"""FastAPI router — Model training and deployment.

Endpoints for training demand forecasting models and testing poster generation.
"""
import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

try:
    from app.ml.dataset_loader import DatasetLoader
    from app.ml.demand_forecasting import DemandForecaster
    from app.ml.image_generation import PosterGenerator
    _ML_AVAILABLE = True
except ImportError:
    _ML_AVAILABLE = False

logger = logging.getLogger(__name__)
router = APIRouter()


# ── Request/Response models ───────────────────────────────────────────────────

class TrainDemandForecastRequest(BaseModel):
    region: str = "all"  # Region filter or "all"
    n_synthetic_records: int = 5000


class TrainDemandForecastResponse(BaseModel):
    status: str
    metrics: dict
    message: str


class GeneratePosterRequest(BaseModel):
    prompt: str
    height: int = 768
    width: int = 512
    num_steps: int = 20


class GeneratePosterResponse(BaseModel):
    status: str
    image_base64: str | None = None
    file_path: str | None = None
    message: str


# ── Training endpoints ────────────────────────────────────────────────────────

@router.post("/train-demand-forecast", response_model=TrainDemandForecastResponse)
def train_demand_forecast(payload: TrainDemandForecastRequest) -> TrainDemandForecastResponse:
    """Train XGBoost demand forecasting model on Indian e-commerce sales data.

    Generates synthetic data if real Kaggle data is not available.
    """
    if not _ML_AVAILABLE:
        raise HTTPException(
            status_code=501,
            detail="ML dependencies not installed: pip install -r requirements_ml.txt"
        )

    try:
        logger.info(f"Training demand forecast (region={payload.region})")

        # Load or generate data
        loader = DatasetLoader()
        df_sales = loader.generate_synthetic_sales_data(n_records=payload.n_synthetic_records)

        # Prepare features
        target_region = None if payload.region == "all" else payload.region
        X, y = loader.get_features_for_model(df_sales, target_region)

        # Train model
        forecaster = DemandForecaster()
        metrics = forecaster.train(X, y, n_estimators=100, max_depth=6)

        # Save trained model
        forecaster.save()

        # Get feature importance
        top_features = forecaster.get_feature_importance(top_n=5)

        return TrainDemandForecastResponse(
            status="success",
            metrics={**metrics, "top_features": top_features},
            message=f"Model trained on {len(df_sales)} records. RMSE={metrics['rmse']}, R²={metrics['r2']}"
        )

    except Exception as e:
        logger.exception("Training failed")
        raise HTTPException(status_code=500, detail=str(e)) from e


# ── Image generation endpoints ────────────────────────────────────────────────

@router.post("/generate-poster", response_model=GeneratePosterResponse)
async def generate_poster(payload: GeneratePosterRequest) -> GeneratePosterResponse:
    """Generate a campaign poster from a text prompt using Stable Diffusion.

    First time usage downloads the model (~8–12 GB) — this will take 5–10 minutes.
    Requires GPU with 8GB+ VRAM. Can run on CPU but will be very slow.

    Example prompt:
        "Indian festival e-commerce poster, cotton sarees, Diwali lamps, 
         vibrant golds and reds, professional design, text overlay area"
    """
    if not _ML_AVAILABLE:
        raise HTTPException(
            status_code=501,
            detail="ML dependencies not installed: pip install -r requirements_ml.txt"
        )

    try:
        logger.info(f"Generating poster: {payload.prompt[:60]}...")

        generator = PosterGenerator(model_id="stabilityai/stable-diffusion-xl-base-1.0")
        image = generator.generate(
            prompt=payload.prompt,
            height=payload.height,
            width=payload.width,
            num_steps=payload.num_steps,
        )

        # Save to file
        output_dir = Path(__file__).resolve().parents[2] / "generated_posters"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / "generated_poster.png"
        generator.save_poster(image, output_file)

        # Also return base64 for API response
        image_base64 = generator.image_to_base64(image)

        return GeneratePosterResponse(
            status="success",
            image_base64=image_base64[:200] + "..." if len(image_base64) > 200 else image_base64,
            file_path=str(output_file),
            message=f"Poster generated successfully. Saved to {output_file}"
        )

    except Exception as e:
        logger.exception("Poster generation failed")
        raise HTTPException(status_code=500, detail=str(e)) from e


# ── Health check ──────────────────────────────────────────────────────────────

@router.get("/ml-status")
def check_ml_status() -> dict:
    """Check if ML dependencies are available."""
    return {
        "ml_available": _ML_AVAILABLE,
        "message": (
            "ML dependencies installed" if _ML_AVAILABLE
            else "ML dependencies NOT installed: pip install -r requirements_ml.txt"
        )
    }
