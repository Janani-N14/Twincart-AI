# TwinCart AI — Hyperlocal Digital Twin & Agentic AI Platform for Bharat Commerce

TwinCart AI creates **Hyperlocal Regional Digital Twins** and **Customer Segment Twins** that continuously learn from sales, weather, festival, and campaign data. A network of specialised Agentic AI agents — orchestrated with LangGraph — detects trends, forecasts demand, generates hyperlocal campaigns and banners, optimises budgets, and runs "what-if" simulations before any real spend is committed.

## Stack

| Layer | Technology |
|-------|-----------|
| Backend API | FastAPI + Pydantic v2 |
| Agent Orchestration | LangGraph |
| LLM Framework | LangChain + langchain-groq |
| LLM Provider | Groq API (free tier) |
| Frontend | Streamlit |

## Quick Start

### 1. Clone & setup environment

```bash
cd TwinCart AI
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
```

### 3. Configure Groq API key

```bash
cp backend/.env.example backend/.env
# Edit backend/.env and add your GROQ_API_KEY from https://console.groq.com
```

### 4. Start the backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

API docs available at: http://localhost:8000/docs

### 5. Start the frontend (new terminal)

```bash
cd frontend
streamlit run streamlit_app.py
```

Open: http://localhost:8501

## Project Structure

```
TwinCart AI/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI entrypoint
│   │   ├── config.py               # Settings (pydantic-settings)
│   │   ├── core/                   # LLM client, logging, exceptions, cache
│   │   ├── models/                 # Pydantic schemas
│   │   ├── twins/                  # Digital Twin domain logic
│   │   ├── agents/                 # LangChain-powered agent nodes
│   │   ├── graph/                  # LangGraph state + workflow
│   │   ├── simulation/             # What-If simulation engine
│   │   ├── routers/                # FastAPI route handlers
│   │   ├── services/               # Orchestrator glue layer
│   │   └── data/                   # Seed JSON datasets
│   └── tests/
├── frontend/
│   ├── streamlit_app.py            # Landing page
│   ├── pages/                      # Multi-page Streamlit UI
│   └── utils/api_client.py         # Backend API wrapper
└── README.md
```

## Running Tests

```bash
cd backend
pytest                        # unit tests only (no LLM calls)
pytest -m live                # include live Groq API smoke tests
```
