"""Phase 2 Unit Tests: Machine Learning Models & Training Pipeline.

Verifies:
- XGBoost demand model loads and computes 7-day forward forecasts
- Point forecasts contain valid numbers and non-negative empirical uncertainty bounds
- Backtested metrics in metrics.json are valid and MAPE is below sanity threshold (<35%)
- Retrain pipeline updates metrics and runs cleanly
"""

import json
from pathlib import Path
import numpy as np
import pytest

from app.ml.demand_forecasting import DemandForecaster, demand_forecaster
from app.ml.train import run_training
from app.ml.retrain import append_new_sales_and_retrain

ML_DIR = Path(__file__).resolve().parents[1] / "app" / "ml"
METRICS_FILE = ML_DIR / "metrics.json"
XGB_MODEL_FILE = ML_DIR / "models" / "xgb_demand.json"


def test_metrics_json_integrity_and_sanity_threshold():
    """Verify metrics.json exists and backtested MAPE is below 35% sanity threshold."""
    assert METRICS_FILE.exists(), f"metrics.json missing at {METRICS_FILE}"
    metrics = json.loads(METRICS_FILE.read_text(encoding="utf-8"))

    assert "mape_percent" in metrics
    assert "rmse_inr" in metrics
    assert "r2_score" in metrics
    assert "residual_std" in metrics

    mape = metrics["mape_percent"]
    assert 0.0 < mape < 35.0, f"MAPE {mape}% exceeds sanity threshold of 35%"
    assert metrics["r2_score"] > 0.5, f"R² score {metrics['r2_score']} should be > 0.5"
    assert metrics["residual_std"] > 0, "Residual standard deviation must be positive"


def test_xgboost_model_file_exists():
    """Verify persisted XGBoost model file exists."""
    assert XGB_MODEL_FILE.exists(), f"xgb_demand.json missing at {XGB_MODEL_FILE}"


def test_demand_forecaster_inference():
    """Verify DemandForecaster produces point forecast and empirical uncertainty bounds."""
    forecaster = DemandForecaster()
    forecaster.load_default_model()

    result = forecaster.forecast_demand(
        region_id="TN-01",
        category="apparel",
        segment_id="students",
        horizon_days=7,
        temperature=30.0,
        is_festival_week=1,
    )

    assert "point_forecast" in result
    assert "uncertainty_lower" in result
    assert "uncertainty_upper" in result
    assert "uncertainty_std" in result
    assert "backtested_mape" in result
    assert result["source"] == "model"

    assert result["point_forecast"] > 0
    assert result["uncertainty_lower"] >= 0
    assert result["uncertainty_upper"] >= result["point_forecast"]
    assert result["uncertainty_std"] > 0
    assert result["horizon_days"] == 7


def test_forecast_horizon_scaling():
    """Verify horizon scaling appropriately scales point forecasts and uncertainty bands."""
    forecaster = DemandForecaster()
    forecaster.load_default_model()

    res_7d = forecaster.forecast_demand(region_id="MH-01", category="beauty", horizon_days=7)
    res_14d = forecaster.forecast_demand(region_id="MH-01", category="beauty", horizon_days=14)

    assert res_14d["point_forecast"] > res_7d["point_forecast"]
    assert res_14d["uncertainty_std"] > res_7d["uncertainty_std"]


def test_retrain_pipeline():
    """Verify retrain pipeline runs and returns updated metrics."""
    res = append_new_sales_and_retrain(new_sales_df=None)
    assert "mape_percent" in res
    assert "retrained_at" in res
    assert res["mape_percent"] < 35.0
