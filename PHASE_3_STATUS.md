# Phase 3 Status: Agent Network & LangGraph Orchestrator

**Status**: ✅ COMPLETE & VERIFIED

## What Works
1. **Trend Detection Agent (`backend/app/agents/trend_detection.py`)**:
   - Calculates statistical 7-day rolling growth rates from actual sales data as a grounded numeric confidence source.
   - Infers emerging trend tags with Groq LLM (and deterministic rule-based fallback).
2. **Demand Forecasting Agent (`backend/app/agents/demand_forecasting.py`)**:
   - Wraps the trained XGBoost model and regional seasonal models.
   - Generates 7-day revenue point forecasts (INR) + empirical uncertainty bands (`± ₹18,826.27` residual std).
   - Surfaces honest model MAPE (`8.94%`) with `source: "model"`.
3. **Scenario Simulation Engine (`backend/app/simulation/engine.py`)**:
   - Computes What-If perturbation scenarios across 4 axes:
     - **Festival Surges**: Exact multipliers from `festivals.json`
     - **Weather & Temperature**: +1.8% demand per +1°C for summer wear, cold penalties on heavy wear
     - **Budget Adjustments**: Marketing mix ROI curve with diminishing returns (`(budget_mult)^0.65 - 1`)
     - **Inventory Shortfalls**: Stockout penalties with partial cart substitution buffer
   - Generates before/after revenue deltas and stores runs with unique `sim_id`.
4. **Campaign Generation Agent (`backend/app/agents/campaign_generator.py`)**:
   - Uses versioned prompt template (`backend/app/prompts/campaign_prompt.txt`).
   - Generates bilingual copy in English and local vernacular language (Tamil, Hindi, Telugu, Marathi, Bengali, Malayalam, Kannada, Gujarati, Odia, Punjabi).
   - Formulates headlines, persuasive copy, CTAs, selling points, and target channels.
5. **Budget Optimization Agent (`backend/app/agents/budget_optimizer.py`)**:
   - Solves constrained linear programming (`scipy.optimize.linprog` with Highs solver) maximizing blended ROI across 5 channels (Social Reels, WhatsApp Community, Search Ads, In-App Push, Regional Influencers).
   - Outputs channel percentages and exact INR amounts for a given total budget.
6. **Explainable AI Agent (`backend/app/agents/explainability.py`)**:
   - Uses versioned prompt template (`backend/app/prompts/explainability_prompt.txt`).
   - Translates upstream model metrics (baseline forecast, simulated forecast, delta amount, MAPE, uncertainty std, festival flags, temp) into clear, plain-language business explanations without hallucinating fake percentages.
7. **Seller Growth Agent (`backend/app/agents/seller_intelligence.py`)**:
   - Uses versioned prompt template (`backend/app/prompts/seller_prompt.txt`).
   - Integrates 7-day demand forecasts, price sensitivity, and category benchmark pricing percentiles (25th, 50th, 75th percentiles from data) to answer seller business questions.
8. **Supervisor / LangGraph Orchestrator (`backend/app/graph/workflow.py`)**:
   - Asynchronous state machine connecting all agents in a fan-out / fan-in pipeline.
9. **Unit Tests (`backend/tests/test_agents.py`)**:
   - 10 unit tests covering every agent and simulation scenario passing cleanly.

## Mocked / Offline Aspects
- Every agent is equipped with deterministic offline fallbacks that activate seamlessly whenever Groq API keys are absent or network requests fail.

## What's Next
- **Phase 4**: FastAPI Backend API Endpoints & REST Layer (`/health`, `/api/twins/*`, `/api/campaigns/*`, `/api/simulation/*`, `/api/sellers/*`, `/api/ml/metrics`).
