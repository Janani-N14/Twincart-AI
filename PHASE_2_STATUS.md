# Phase 2 Status: Machine Learning Models & Training Pipeline

**Status**: ✅ COMPLETE & VERIFIED

## What Works
1. **XGBoost Demand Regression Model (`backend/app/ml/train.py`)**:
   - Trained on 116,960 train records (2023-2024) and evaluated on 58,400 held-out test records (2025).
   - Features: region, segment, category, population tier (encoded), day-of-week, month, day-of-year, temperature, weekend indicator, festival indicators, days to festival, and rolling 7/14/28-day sales volume.
   - Evaluated honestly on held-out test split:
     - **MAPE**: **8.94%** (well below the <35% sanity threshold)
     - **R² Score**: **0.9535**
     - **RMSE**: **₹18,875.50**
     - **Residual Standard Deviation**: **₹18,826.27** (used as empirical uncertainty band)
   - Model saved to `backend/app/ml/models/xgb_demand.json` and `backend/app/ml/models/xgb_demand.pkl`.
   - Metrics saved to `backend/app/ml/metrics.json`.
2. **Regional Seasonal Models**:
   - 64 regional category seasonal models fitted and saved under `backend/app/ml/models/seasonal/`.
   - Captures monthly baselines, day-of-week patterns, and regional festival uplift factors.
3. **Inference & Uncertainty Bounds (`backend/app/ml/demand_forecasting.py`)**:
   - Exposes `DemandForecaster` with `forecast_demand(...)` returning:
     - `point_forecast` (estimated sales in INR)
     - `uncertainty_lower` and `uncertainty_upper` (empirical 95% confidence interval derived from backtest residuals)
     - `uncertainty_std`
     - `backtested_mape` (honest MAPE metric)
     - `source: "model"`
4. **Retraining Pipeline (`backend/app/ml/retrain.py`)**:
   - Batch retraining pipeline supporting incremental new sales appending and re-fitting of both model families.
5. **Unit Tests (`backend/tests/test_ml.py`)**:
   - 5 comprehensive tests verifying metrics integrity, model persistence, point predictions + uncertainty bounds, horizon scaling, and retraining. All passed.

## Mocked / Offline Aspects
- None. Model training, inference, feature engineering, and metrics evaluation are 100% offline and deterministic.

## What's Next
- **Phase 3**: Agent Network & LangGraph Orchestrator (Trend Detection, Demand Forecasting Agent, Scenario Simulation Engine, Campaign Generation Agent, Budget Optimization Agent, Explainable AI Agent, Seller Growth Agent, Supervisor Orchestrator).
