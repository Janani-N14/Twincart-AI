"""Page 4 — What-If Scenario Simulation Engine.

Interactive scenario testing across Festival surges, Climate shifts, Budget scaling,
and Stockouts with explicit mathematical elasticity.
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.api_client import list_regions, run_simulation

st.set_page_config(page_title="Simulation Engine · TwinCart AI", page_icon="🔮", layout="wide")

st.markdown(
    """
    <style>
    .disclosure-pill {
        background: rgba(255, 107, 53, 0.12);
        border: 1px solid rgba(255, 107, 53, 0.4);
        color: #FFA585;
        padding: 0.3rem 0.8rem;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 0.8rem;
    }
    .provenance-tag {
        font-size: 0.75rem;
        padding: 0.2rem 0.6rem;
        border-radius: 4px;
        background: rgba(46, 134, 171, 0.2);
        color: #70C1B3;
        border: 1px solid rgba(46, 134, 171, 0.4);
        display: inline-block;
        margin-bottom: 0.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="disclosure-pill">Demo dataset — synthetic data</div>', unsafe_allow_html=True)
st.title("🔮 What-If Scenario Simulation Engine")
st.caption("Perturb demand variables and observe immediate revenue and conversion impacts with mathematically traceable multipliers.")

# ── Load Regions ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def _regions():
    return list_regions()

try:
    regions = _regions()
except Exception as e:
    st.error(f"Could not reach backend: {e}")
    st.stop()

region_map = {f"{r['state']} — {r.get('city', r['region_id'])}": r["region_id"] for r in regions}

# ── Scenario Configuration ────────────────────────────────────────────────────
st.markdown("### 🎛️ Configure Scenario Perturbation")

col_reg, col_cat, col_type = st.columns(3)
with col_reg:
    selected_region = st.selectbox("Target Region", list(region_map.keys()), index=0)
    region_id = region_map[selected_region]

with col_cat:
    category = st.selectbox("Product Category", ["apparel", "ethnic wear", "footwear", "beauty", "home textiles"], index=0)

with col_type:
    scenario_type = st.selectbox(
        "Perturbation Axis",
        [
            "festival (Upcoming Regional Festival)",
            "weather (Temperature Anomaly)",
            "budget (Ad Spend Scaling)",
            "inventory (Stockout & Out-of-Stock)",
        ],
        index=0,
    )
    clean_scenario = scenario_type.split()[0]

st.write("")
# Perturbation Magnitude Slider
if clean_scenario == "festival":
    magnitude = st.slider("🎉 Festival Demand Surge Intensity (%)", min_value=10.0, max_value=80.0, value=35.0, step=5.0)
elif clean_scenario == "weather":
    magnitude = st.slider("🌡️ Temperature Deviation (°C from monthly baseline)", min_value=-12.0, max_value=12.0, value=4.0, step=0.5)
elif clean_scenario == "budget":
    magnitude = st.slider("💰 Marketing Ad Spend Change (%)", min_value=-60.0, max_value=150.0, value=40.0, step=10.0)
else: # inventory
    magnitude = st.slider("📦 Unmet Inventory Shortfall (% out of stock)", min_value=5.0, max_value=70.0, value=25.0, step=5.0)

st.write("")
sim_btn = st.button("▶ Run Mathematical Simulation", type="primary", use_container_width=True)

if sim_btn or "last_sim" in st.session_state:
    if sim_btn:
        with st.spinner("Calculating empirical demand perturbation and elasticities..."):
            try:
                res = run_simulation(
                    region_id=region_id,
                    category=category,
                    scenario=clean_scenario,
                    magnitude=float(magnitude),
                )
                st.session_state["last_sim"] = res
            except Exception as e:
                st.error(f"Simulation execution failed: {e}")
                st.stop()
    else:
        res = st.session_state["last_sim"]

    st.divider()
    st.markdown(f"### 📊 Simulation Outcomes: `{res.get('sim_id', 'sim_001')}`")

    # ── KPI Cards ─────────────────────────────────────────────────────────────
    base_rev = float(res.get("baseline_forecast", 145000.0))
    sim_rev = float(res.get("simulated_forecast", 175000.0))
    delta_inr = float(res.get("delta_amount", sim_rev - base_rev))
    delta_pct = float(res.get("delta_percent", 20.0))
    conv_rate = float(res.get("predicted_conversion_rate", 0.42))
    rev_index = float(res.get("predicted_revenue_index", 120.0))

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric(
            label="Baseline 7-Day Revenue",
            value=f"₹{base_rev:,.0f}",
            delta="XGBoost Baseline",
        )
    with k2:
        st.metric(
            label="Simulated 7-Day Revenue",
            value=f"₹{sim_rev:,.0f}",
            delta=f"{delta_pct:+.1f}% (₹{delta_inr:+,.0f})",
            delta_color="normal" if delta_pct >= 0 else "inverse",
        )
    with k3:
        st.metric(
            label="Predicted Conversion",
            value=f"{conv_rate:.1%}",
            delta="Elasticity Adjusted",
        )
    with k4:
        st.metric(
            label="Revenue Index",
            value=f"{rev_index:.1f}",
            delta="100.0 = Baseline",
        )

    st.write("")

    # ── Before vs After Waterfall / Comparison ────────────────────────────────
    col_chart, col_gauge = st.columns([1.4, 1.0])

    with col_chart:
        st.markdown("#### 📈 Revenue Comparison (₹ INR)")
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            x=["Baseline Model Forecast", "Simulated Scenario Forecast"],
            y=[base_rev, sim_rev],
            text=[f"₹{base_rev:,.0f}", f"₹{sim_rev:,.0f} ({delta_pct:+.1f}%)"],
            textposition="auto",
            marker_color=["#2E86AB", "#FF6B35" if delta_pct >= 0 else "#E63946"],
        ))
        fig_bar.update_layout(
            template="plotly_dark",
            yaxis_title="Estimated 7-Day Revenue (₹)",
            height=300,
            margin=dict(l=10, r=10, t=10, b=10),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_gauge:
        st.markdown("#### 🎯 Revenue Index Meter")
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=rev_index,
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [0, 200]},
                'bar': {'color': "#2A9D8F" if rev_index >= 100 else "#E76F51"},
                'steps': [
                    {'range': [0, 80], 'color': "rgba(230, 57, 70, 0.25)"},
                    {'range': [80, 120], 'color': "rgba(244, 162, 97, 0.25)"},
                    {'range': [120, 200], 'color': "rgba(42, 157, 143, 0.25)"},
                ],
                'threshold': {
                    'line': {'color': "white", 'width': 4},
                    'thickness': 0.75,
                    'value': 100.0,
                },
            },
        ))
        fig_gauge.update_layout(
            template="plotly_dark",
            height=300,
            margin=dict(l=10, r=10, t=10, b=10),
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

    # ── Explainability & Elasticity Multipliers ───────────────────────────────
    st.write("")
    st.markdown("### 🔍 Traceable Elasticity Factors & Reasoning")
    st.markdown('<div class="provenance-tag">Source: Synthetic Data Elasticity Parameters & Grounded Explainability</div>', unsafe_allow_html=True)

    st.success(f"**Scenario Interpretation:** {res.get('interpretation', '')}")

    factors = res.get("elasticity_factors", {})
    if factors:
        with st.expander("🔬 View Mathematical Elasticity Coefficients", expanded=True):
            st.json(factors)
