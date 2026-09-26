# 🛍️ TwinCart AI (TwinAI)

> **Hyperlocal Digital Twin & Agentic AI Demand Platform for Bharat E-Commerce**  
> *Autonomous Demand Forecasting, What-If Scenario Simulation, and Localized Vernacular Marketing for Indian Tier-2/3 Trade Hubs.*

[![Backend Tests](https://img.shields.io/badge/backend%20tests-50%2F50%20passed-brightgreen.svg)]()
[![Model Backtested MAPE](https://img.shields.io/badge/XGBoost%20MAPE-8.94%25-blue.svg)]()
[![Model R² Accuracy](https://img.shields.io/badge/R%C2%B2%20Score-0.9535-purple.svg)]()
[![Orchestration](https://img.shields.io/badge/Agents-LangGraph-orange.svg)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-v0.115-009688.svg)]()
[![UI](https://img.shields.io/badge/UI-HTML5%20%2B%20Streamlit-FF4B4B.svg)]()

---

## 🧭 Table of Contents

1. [Architecture Diagram](#-architecture-diagram)
2. [Backend Flow & Multi-Agent Process](#-backend-flow--multi-agent-process)
3. [Machine Learning Models & Backtested Performance](#-machine-learning-models--backtested-performance)
4. [What-If Scenario Simulation Engine](#-what-if-scenario-simulation-engine)
5. [Digital Twin Domain Stores](#-digital-twin-domain-stores)
6. [User Interfaces (HTML5 Web App & Streamlit)](#-user-interfaces)
7. [API Reference & Provenance Mapping](#-api-reference--provenance-mapping)
8. [Quickstart & Testing](#-quickstart--testing)
9. [Zero-Fabricated-Metrics Policy](#-zero-fabricated-metrics-policy)

---

## 🏗️ Architecture Diagram

```mermaid
graph TD
    subgraph "Presentation Layer (Dual UI)"
        WEB["🌐 HTML5 / Vanilla CSS / JS Single-Page App<br/>(http://localhost:8000/)"]
        STREAMLIT["📊 Streamlit Multipage Application<br/>(http://localhost:8501/)"]
    end

    subgraph "API Gateway Layer (FastAPI)"
        ROUTER["FastAPI Router Gateway<br/>/api/twins | /api/campaigns | /api/simulation | /api/sellers"]
    end

    WEB --> ROUTER
    STREAMLIT --> ROUTER

    subgraph "Agentic Network (LangGraph StateGraph)"
        STATE["TwinAIState Data Container"]
        ROUTER --> STATE
        
        STATE --> N1["1. Trend Detection Agent<br/>14-Day Growth Stats + Vernacular Tagging"]
        N1 --> N2["2. Demand Forecasting Agent<br/>XGBoost Model Wrapper + Residual Std Error"]
        N2 --> N3["3. Campaign Generator Agent<br/>Groq LLM / Bilingual English + Vernacular Engine"]
        N3 --> N4["4. Budget Optimization Agent<br/>SciPy Linear Programming (linprog / Highs)"]
        N4 --> N5["5. Explainable AI Agent<br/>Grounded Factor Provenance (Zero Hallucinations)"]
        
        ROUTER -.-> N6["6. Seller Intelligence Advisor<br/>Percentile Price Benchmarks (p25, p50, p75)"]
    end

    subgraph "Simulation & ML Engine"
        SIM["What-If Simulation Engine<br/>Festival, Weather, Budget, Stockout Elasticities"]
        XGB["XGBoost Demand Regressor<br/>(MAPE: 8.94% | R²: 0.9535)"]
        SEASONAL["64 Regional Seasonal Models"]
        DATA[("Synthetic Bharat Dataset<br/>175,360 rows | 16 Regions | 5 Segments")]
    end

    N2 --> XGB
    SIM --> DATA
    SIM --> XGB
    N6 --> DATA
    N6 --> XGB
    ROUTER --> SIM
```

---

## 🔄 Backend Flow & Multi-Agent Process

The backend operates on an asynchronous event-driven pipeline orchestrated by **LangGraph** with strict typed state transitions (`TwinAIState`).

### Detailed Request-to-Response Lifecycle

```mermaid
sequenceDiagram
    autonumber
    actor User as User / Client
    participant Router as FastAPI Router
    participant Orchestrator as LangGraph StateGraph
    participant Trend as Trend Agent
    participant Demand as Demand ML Agent
    participant Campaign as Campaign LLM Agent
    participant Budget as SciPy Optimizer
    participant Explain as Explainability Agent
    participant Response as Client Response

    User->>Router: POST /api/campaigns/generate (region_id, segment_id, category, budget)
    Router->>Orchestrator: Initialize TwinAIState
    
    Orchestrator->>Trend: 1. Compute 14-day rolling growth rates from synthetic data
    Trend-->>Orchestrator: Return trends & numeric growth rates
    
    Orchestrator->>Demand: 2. Invoke XGBoost model with climate & festival calendar features
    Demand-->>Orchestrator: Return point forecast (₹) + uncertainty band (±1.96σ)
    
    Orchestrator->>Campaign: 3. Query Groq LLM / Vernacular engine for bilingual copy & banner briefs
    Campaign-->>Orchestrator: Return English & Regional copy (Tamil, Marathi, Hindi, Telugu, Kannada)
    
    Orchestrator->>Budget: 4. Execute SciPy linprog (Highs solver) for constrained ROI maximization
    Budget-->>Orchestrator: Return channel allocations & exact INR spend amounts
    
    Orchestrator->>Explain: 5. Format grounded explanation citing upstream factors
    Explain-->>Orchestrator: Return plain-language reasoning with zero hallucinations
    
    Orchestrator-->>Router: Finalize assembled state with source provenance tags
    Router-->>Response: 200 OK JSON with per-claim provenance ("model", "heuristic", "llm_explanation")
```

### LangGraph State Machine Nodes:
1. **Trend Detection Agent** ([trend_detection.py](file:///c:/Users/njana/Music/twincart/backend/app/agents/trend_detection.py)): Extracts recent sales windows for the target district and computes week-over-week growth rates without LLM hallucinations.
2. **Demand Forecasting Agent** ([demand_forecasting.py](file:///c:/Users/njana/Music/twincart/backend/app/agents/demand_forecasting.py)): Wraps the trained XGBoost model, feeding region, segment, category, temperature, and festival indicators. Returns point forecast and empirical residual uncertainty.
3. **Campaign Generation Agent** ([campaign_generator.py](file:///c:/Users/njana/Music/twincart/backend/app/agents/campaign_generator.py)): Generates culturally resonant ad copy in English and the district's local language (using Groq LLM with deterministic offline fallbacks).
4. **Budget Optimization Agent** ([budget_optimizer.py](file:///c:/Users/njana/Music/twincart/backend/app/agents/budget_optimizer.py)): Solves a bounded linear programming problem (`scipy.optimize.linprog` with `method="highs"`) allocating budget across Social Media, Regional Search, Vernacular Push, SMS/WhatsApp, and Micro-Influencers.
5. **Explainable AI Agent** ([explainability.py](file:///c:/Users/njana/Music/twincart/backend/app/agents/explainability.py)): Takes the numerical factors (festival boost %, temperature delta, baseline demand, budget ROI) and generates plain-language business reasoning.
6. **Seller Intelligence Advisor** ([seller_intelligence.py](file:///c:/Users/njana/Music/twincart/backend/app/agents/seller_intelligence.py)): Computes 25th, 50th (median), and 75th percentile market prices for the category to deliver grounded margin and stocking strategies.

---

## 🤖 Machine Learning Models & Backtested Performance

### 1. XGBoost Short-Horizon Demand Regressor (`xgb_demand.json`)
- **Objective**: Predict 7-day forward sales volume and revenue for any (district $\times$ segment $\times$ category) combination.
- **Features (11 engineered features)**:
  - `region_encoded`, `segment_encoded`, `category_encoded` (Categorical entity embeddings)
  - `day_of_week`, `month`, `quarter` (Temporal seasonality)
  - `rolling_7d_avg`, `rolling_14d_avg`, `rolling_28d_avg` (Historical demand momentum)
  - `avg_temperature_c` (Climate sensitivity)
  - `is_festival_week`, `days_to_next_festival` (Cultural demand surges)
- **Time-Based Validation Split**:
  - **Train**: 2023–2024 (116,960 data points)
  - **Held-Out Test**: Full year 2025 (58,400 data points) — *never random shuffled*.

### Verified Model Performance ([metrics.json](file:///c:/Users/njana/Music/twincart/backend/app/ml/metrics.json)):
| Metric | Backtested Value | Benchmark / Sanity Standard |
| :--- | :--- | :--- |
| **MAPE (Mean Absolute Percentage Error)** | **8.94%** | Sanity Threshold < 35.0% ✅ |
| **Coefficient of Determination ($R^2$)** | **0.9535** | High Accuracy Fit ✅ |
| **RMSE (Root Mean Squared Error)** | **₹18,875.50** | Verified on held-out 2025 test |
| **Empirical Residual Std Dev ($1\sigma$)** | **₹18,826.27** | Used for $\pm 1.96\sigma$ uncertainty bounds |

### 2. Regional Seasonal Time Series Models (64 Models)
- 64 distinct regional category seasonal profiles in `backend/app/ml/models/seasonal/` capturing multi-annual recurring festival and harvest waves.

### 3. Continuous Learning Pipeline (`backend/app/ml/retrain.py`)
- Incremental append and refit pipeline that ingests new sales data and updates backtested metrics without claiming unverified real-time streaming.

---

## 🔮 What-If Scenario Simulation Engine

The What-If engine ([engine.py](file:///c:/Users/njana/Music/twincart/backend/app/simulation/engine.py)) allows category managers and sellers to perturb market variables and observe immediate revenue and conversion impacts:

1. **🎉 Festival Surges**: Applies category-specific upticks directly mapped from [festivals.json](file:///c:/Users/njana/Music/twincart/backend/app/data/festivals.json) (e.g. Pongal $\rightarrow$ cotton/ethnic wear $+38\%$).
2. **🌡️ Temperature Deviations**: Models climate demand shifts ($+1.8\% / ^\circ\text{C}$ for breathable summer cottons; negative penalties on cold-weather apparel).
3. **💰 Ad Budget Scaling**: Models marketing ROI with diminishing returns curve: $\text{Multiplier} = (\text{Spend Ratio})^{0.65} - 1.0$.
4. **📦 Inventory Shortfalls**: Computes unmet demand loss with partial substitution elasticity: $\text{Penalty} = -\text{Shortfall} \times 0.88$.

---

## 👥 Digital Twin Domain Stores

### 16 Indian Tier-2/3 Regional District Twins ([regions.json](file:///c:/Users/njana/Music/twincart/backend/app/data/regions.json)):
- **South**: Madurai (TN), Salem (TN), Hubballi-Dharwad (KA), Belagavi (KA), Kozhikode (KL), Thrissur (KL), Warangal (TG), Guntur (AP).
- **West & Central**: Kolhapur (MH), Solapur (MH), Jodhpur (RJ), Udaipur (RJ), Ujjain (MP), Gwalior (MP).
- **North & East**: Patiala (PB), Muzaffarpur (BR).

### 5 Localized Consumer Personas ([segments.json](file:///c:/Users/njana/Music/twincart/backend/app/data/segments.json)):
1. **College Students & Gen-Z** (`students`): High price sensitivity (85%), basket ₹300–₹1,200, driven by flash sales and Instagram trends.
2. **Early-Career Professionals** (`working_professionals`): Moderate sensitivity (52%), basket ₹1,000–₹3,500, driven by payday sales and workwear quality.
3. **Family Homemakers & Curators** (`homemakers`): High sensitivity (78%), basket ₹500–₹2,500, driven by festival combo sets and longevity.
4. **Bargain Hunters & Tier-3 Aspirants** (`budget_shoppers`): Maximum sensitivity (92%), basket ₹200–₹800, driven by >50% discounts and COD.
5. **Young Parents & Modern Families** (`young_parents`): Moderate sensitivity (60%), basket ₹800–₹3,000, driven by season shifts and kids comfort guarantees.

---

## 💻 User Interfaces

TwinCart AI provides **dual interfaces**:

### 1. Embedded HTML5 / Vanilla CSS / JavaScript Single-Page Application
- Served directly by FastAPI at **`http://localhost:8000/`**.
- Powered by Chart.js, glassmorphism CSS design system, dark mode styling, and live API connectivity.

### 2. Streamlit Multipage Application
- Served at **`http://localhost:8501/`**.
- 5 comprehensive pages with Plotly interactive visualizations.

---

## 📡 API Reference & Provenance Mapping

Every numeric prediction in the API returns an explicit `sources` dictionary mapping each claim to its origin:

| Method | Endpoint | Description | Provenance Source |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Liveness probe & system environment | `system` |
| `GET` | `/api/twins/regions` | List 16 regional district twins | `data_store` |
| `GET` | `/api/twins/regions/{id}` | Get specific district twin profile | `data_store` |
| `GET` | `/api/twins/segments` | List 5 customer segment personas | `data_store` |
| `GET` | `/api/twins/segments/{id}` | Get specific persona details | `data_store` |
| `POST` | `/api/campaigns/generate` | Run full LangGraph campaign pipeline | `"model"`, `"heuristic_optimization"`, `"llm_explanation"` |
| `GET` | `/api/campaigns/{id}` | Retrieve cached campaign by ID | `cache` |
| `POST` | `/api/simulation/run` | Execute What-If scenario perturbation | `"model"`, `"heuristic"` (explicit elasticities) |
| `GET` | `/api/simulation/{id}` | Retrieve simulation run by ID | `cache` |
| `POST` | `/api/sellers/ask` | Natural-language seller growth advisor | `"model"`, `"heuristic"` (p25/p50/p75 percentiles) |
| `GET` | `/api/training/metrics` | Model backtest MAPE, $R^2$, RMSE | `model_evaluation` |
| `POST` | `/api/training/retrain` | Incremental model refitting trigger | `ml_pipeline` |

---

## 🚀 Quickstart & Testing

### Option A: Local Python Virtual Environment (< 60 Seconds)

1. **Activate Virtual Environment**:
   ```bash
   # Windows:
   .venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r backend/requirements.txt
   pip install -r frontend/requirements.txt
   ```

3. **Start Full-Stack Backend & HTML Web App**:
   ```bash
   uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
   ```
   - Open **`http://localhost:8000/`** for the HTML5 Web Application.
   - Open **`http://localhost:8000/docs`** for interactive Swagger API documentation.

4. **(Optional) Start Streamlit UI**:
   ```bash
   streamlit run frontend/streamlit_app.py --server.port 8501
   ```

### Option B: Docker Compose
```bash
docker-compose up --build
```

### Run Automated Test Suite (50 Tests, 100% Deterministic)
```bash
pytest backend/tests/ -v
```

---

## 🛡️ Zero-Fabricated-Metrics Policy

- No fabricated confidence percentages (e.g. no random "Confidence: 87%").
- All demand numbers stem directly from the **XGBoost Regressor backtest** or **empirical residual standard error bounds**.
- What-If simulations trace back to explicitly defined parameters in `festivals.json` and data generator elasticity multipliers.
- Built-in deterministic fallbacks ensure 100% functionality even during offline execution or missing API keys.
