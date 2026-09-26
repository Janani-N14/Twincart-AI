"""ML Training Pipeline for TwinCart AI.

Trains two model families on synthetic_sales.csv:
1. XGBoost Demand Regressor:
   - Predicts 7-day forward demand per (region, segment, category)
   - Features: encoded region, segment, category, day-of-week, month,
     rolling 7/14/28-day sales averages, temperature, days_to_next_festival,
     is_festival_week.
   - Time-based train/test split (2023-2024 train, 2025 test).
   - Evaluates MAPE and RMSE on held-out test set; persists metrics to metrics.json
   - Persists model to models/xgb_demand.json and models/xgb_demand.pkl.

2. Seasonal / Festival Regional Models:
   - Fits regional category time-series models capturing festival and seasonal patterns.
   - Persists to models/seasonal/{region_id}_{category}.pkl.

Run with: python backend/app/ml/train.py
"""

import json
import logging
import pickle
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

ML_DIR = Path(__file__).resolve().parent
DATA_DIR = ML_DIR.parent / "data"
CSV_PATH = DATA_DIR / "synthetic_sales.csv"
MODELS_DIR = ML_DIR / "models"
SEASONAL_MODELS_DIR = MODELS_DIR / "seasonal"
METRICS_FILE = ML_DIR / "metrics.json"


def prepare_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, LabelEncoder]]:
    """Build time-series and contextual features with time-lagged rolling windows."""
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["region_id", "category", "segment_id", "date"]).reset_index(drop=True)

    # Encode categorical features
    encoders: Dict[str, LabelEncoder] = {}
    for col in ["region_id", "segment_id", "category", "population_tier"]:
        le = LabelEncoder()
        df[f"{col}_encoded"] = le.fit_transform(df[col].astype(str))
        encoders[col] = le

    # Date temporal features
    df["day_of_week"] = df["date"].dt.dayofweek
    df["month"] = df["date"].dt.month
    df["day_of_year"] = df["date"].dt.dayofyear

    # Rolling sales averages per (region, category, segment)
    grouped = df.groupby(["region_id", "category", "segment_id"])["daily_sales"]
    df["rolling_7d_sales"] = grouped.transform(lambda s: s.shift(1).rolling(7, min_periods=1).mean())
    df["rolling_14d_sales"] = grouped.transform(lambda s: s.shift(1).rolling(14, min_periods=1).mean())
    df["rolling_28d_sales"] = grouped.transform(lambda s: s.shift(1).rolling(28, min_periods=1).mean())

    # Target: Next 7-day forward sales sum
    df["target_7d_sales"] = grouped.transform(
        lambda s: s.shift(-7).rolling(7, min_periods=1).sum()
    ).fillna(df["daily_sales"] * 7)

    # Fill any remaining NaNs
    df["rolling_7d_sales"] = df["rolling_7d_sales"].fillna(df["daily_sales"])
    df["rolling_14d_sales"] = df["rolling_14d_sales"].fillna(df["daily_sales"])
    df["rolling_28d_sales"] = df["rolling_28d_sales"].fillna(df["daily_sales"])

    return df, encoders


def train_xgboost_demand_model(df: pd.DataFrame, encoders: Dict[str, LabelEncoder]) -> Tuple[xgb.XGBRegressor, Dict[str, Any]]:
    """Train XGBoost regressor using time-based train/test split."""
    feature_cols = [
        "region_id_encoded",
        "segment_id_encoded",
        "category_encoded",
        "population_tier_encoded",
        "day_of_week",
        "month",
        "day_of_year",
        "temperature",
        "is_weekend",
        "is_festival_week",
        "days_to_next_festival",
        "rolling_7d_sales",
        "rolling_14d_sales",
        "rolling_28d_sales",
        "avg_price",
    ]

    # Time-based split: Train on years < 2025, Test on 2025
    train_mask = df["date"] < pd.to_datetime("2025-01-01")
    test_mask = df["date"] >= pd.to_datetime("2025-01-01")

    X_train = df.loc[train_mask, feature_cols]
    y_train = df.loc[train_mask, "target_7d_sales"]
    X_test = df.loc[test_mask, feature_cols]
    y_test = df.loc[test_mask, "target_7d_sales"]

    logger.info("XGBoost training set: %d samples, test set: %d samples", len(X_train), len(X_test))

    model = xgb.XGBRegressor(
        n_estimators=150,
        max_depth=6,
        learning_rate=0.08,
        subsample=0.85,
        colsample_bytree=0.85,
        random_state=42,
        tree_method="hist",
        objective="reg:squarederror",
    )

    model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)

    # Evaluate on held-out test split
    y_pred = model.predict(X_test)
    y_pred = np.maximum(y_pred, 1.0)  # non-negative sales

    rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
    r2 = float(r2_score(y_test, y_pred))
    mape = float(mean_absolute_percentage_error(y_test, y_pred) * 100)
    residuals = y_test - y_pred
    residual_std = float(np.std(residuals))

    metrics = {
        "model_type": "XGBoost Regressor (7-day forward demand)",
        "train_samples": int(len(X_train)),
        "test_samples": int(len(X_test)),
        "train_date_range": "2023-01-01 to 2024-12-31",
        "test_date_range": "2025-01-01 to 2025-12-31",
        "mape_percent": round(mape, 2),
        "rmse_inr": round(rmse, 2),
        "r2_score": round(r2, 4),
        "residual_std": round(residual_std, 2),
        "feature_names": feature_cols,
        "features_importance": {
            col: round(float(imp), 4)
            for col, imp in zip(feature_cols, model.feature_importances_)
        },
    }

    logger.info("XGBoost Evaluation: MAPE=%.2f%% | RMSE=₹%.2f | R²=%.4f | Residual Std=₹%.2f", mape, rmse, r2, residual_std)
    return model, metrics


def train_seasonal_models(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """Fit regional category seasonal models for quick holiday and festival what-if forecasts."""
    SEASONAL_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    seasonal_meta = {}

    # Aggregate by (region_id, category, date)
    agg_df = df.groupby(["region_id", "category", "date"]).agg({
        "daily_sales": "sum",
        "units_sold": "sum",
        "temperature": "mean",
        "is_festival_week": "max",
        "is_weekend": "max",
    }).reset_index()

    grouped = agg_df.groupby(["region_id", "category"])

    for (r_id, cat), group in grouped:
        if len(group) < 30:
            continue

        clean_cat = cat.replace(" ", "_").replace("(", "").replace(")", "")
        model_name = f"{r_id}_{clean_cat}.pkl"
        model_file = SEASONAL_MODELS_DIR / model_name

        # Calculate monthly and day-of-week base profiles
        group = group.copy()
        group["month"] = pd.to_datetime(group["date"]).dt.month
        group["dayofweek"] = pd.to_datetime(group["date"]).dt.dayofweek

        monthly_profile = group.groupby("month")["daily_sales"].mean().to_dict()
        dow_profile = group.groupby("dayofweek")["daily_sales"].mean().to_dict()
        festival_uplift = float(
            group[group["is_festival_week"] == 1]["daily_sales"].mean()
            / max(group[group["is_festival_week"] == 0]["daily_sales"].mean(), 1.0)
        )
        base_mean = float(group["daily_sales"].mean())
        base_std = float(group["daily_sales"].std())

        model_payload = {
            "region_id": r_id,
            "category": cat,
            "base_mean": round(base_mean, 2),
            "base_std": round(base_std, 2),
            "monthly_profile": {int(k): round(float(v), 2) for k, v in monthly_profile.items()},
            "dow_profile": {int(k): round(float(v), 2) for k, v in dow_profile.items()},
            "festival_uplift_ratio": round(festival_uplift, 3),
        }

        with open(model_file, "wb") as f:
            pickle.dump(model_payload, f)

        seasonal_meta[f"{r_id}_{cat}"] = {
            "file": model_name,
            "base_mean": round(base_mean, 2),
            "festival_uplift": round(festival_uplift, 3),
        }

    logger.info("Trained %d regional seasonal models in %s", len(seasonal_meta), SEASONAL_MODELS_DIR)
    return seasonal_meta


def run_training():
    """Execute complete training pipeline and persist artifacts."""
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    if not CSV_PATH.exists():
        logger.info("synthetic_sales.csv not found, generating now...")
        from app.data.synthetic_sales import generate_synthetic_sales
        generate_synthetic_sales()

    logger.info("Loading sales data from %s...", CSV_PATH)
    df = pd.read_csv(CSV_PATH)

    logger.info("Engineering features...")
    df_feat, encoders = prepare_features(df)

    logger.info("Training XGBoost demand regressor...")
    xgb_model, metrics = train_xgboost_demand_model(df_feat, encoders)

    # Save XGBoost model in JSON & pickle format
    xgb_json_path = MODELS_DIR / "xgb_demand.json"
    xgb_pkl_path = MODELS_DIR / "xgb_demand.pkl"
    xgb_model.save_model(str(xgb_json_path))

    with open(xgb_pkl_path, "wb") as f:
        pickle.dump({"model": xgb_model, "encoders": encoders, "features": metrics["feature_names"]}, f)

    logger.info("Saved XGBoost model to %s and %s", xgb_json_path, xgb_pkl_path)

    # Train Seasonal Models
    logger.info("Fitting seasonal time-series models per region & category...")
    seasonal_meta = train_seasonal_models(df)

    # Write combined honest metrics to metrics.json
    full_metrics = {
        **metrics,
        "seasonal_models_count": len(seasonal_meta),
        "seasonal_models_sample": list(seasonal_meta.keys())[:10],
    }

    with open(METRICS_FILE, "w", encoding="utf-8") as f:
        json.dump(full_metrics, f, indent=2)

    logger.info("Saved metrics to %s (MAPE: %.2f%%)", METRICS_FILE, metrics["mape_percent"])
    return full_metrics


if __name__ == "__main__":
    run_training()
