"""FastAPI router — Model training, metrics, and deployment."""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from app.ml.demand_forecasting import demand_forecaster
from app.ml.retrain import append_new_sales_and_retrain
from app.ml.train import run_training

logger = logging.getLogger(__name__)
router = APIRouter()

METRICS_FILE = Path(__file__).resolve().parents[1] / "ml" / "metrics.json"


class TrainDemandForecastRequest(BaseModel):
    region: str = "all"
    n_synthetic_records: int = 5000


class TrainDemandForecastResponse(BaseModel):
    status: str
    metrics: Dict[str, Any]
    message: str


@router.get("/metrics", summary="Get model backtested metrics")
def get_model_metrics() -> Dict[str, Any]:
    """Return honest backtested performance metrics (MAPE, RMSE, R², uncertainty bands)
    calculated on the held-out test dataset.
    """
    if METRICS_FILE.exists():
        try:
            return json.loads(METRICS_FILE.read_text(encoding="utf-8"))
        except Exception as e:
            logger.warning("Error reading metrics file: %s", e)
    return demand_forecaster.get_metrics()


@router.post("/train-demand-forecast", response_model=TrainDemandForecastResponse)
def trigger_train_demand_forecast(payload: TrainDemandForecastRequest) -> TrainDemandForecastResponse:
    """Train/retrain XGBoost demand forecasting model on synthetic sales dataset."""
    try:
        metrics = append_new_sales_and_retrain(new_sales_df=None)
        return TrainDemandForecastResponse(
            status="completed",
            metrics=metrics,
            message=f"Model trained successfully. Backtested MAPE: {metrics.get('mape_percent')}%",
        )
    except Exception as exc:
        logger.exception("Training trigger failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc
