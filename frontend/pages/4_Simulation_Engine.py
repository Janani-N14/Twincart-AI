"""Page 4 — What-If Simulation Engine."""
import plotly.graph_objects as go
import streamlit as st
from utils.api_client import list_regions, run_simulation

st.set_page_config(page_title="Simulation Engine · TwinCart AI", page_icon="🔮", layout="wide")
st.title("🔮 What-If Simulation Engine")
st.caption(
    "Adjust scenario variables and instantly see how they affect predicted "
    "conversion rate and revenue index — without spending a single rupee."
)

@st.cache_data(ttl=300)
def _regions():
    return list_regions()

try:
    regions = _regions()
except Exception as e:
    st.error(f"Could not reach backend: {e}")
    st.stop()

region_map = {r["state"]: r["region_id"] for r in regions}

# ── Scenario controls ─────────────────────────────────────────────────────────
st.subheader("Configure Scenario")

col1, col2 = st.columns(2)
with col1:
    selected_state = st.selectbox("Target Region", list(region_map.keys()))
    festival_next_week = st.toggle("🎉 Major festival within next 7 days", value=False)
    temperature_delta = st.slider(
        "🌡️ Temperature deviation from average (°C)",
        min_value=-15.0, max_value=15.0, value=0.0, step=0.5,
    )
with col2:
    budget_multiplier = st.slider(
        "💰 Budget multiplier (1.0 = baseline)",
        min_value=0.1, max_value=5.0, value=1.0, step=0.1,
    )
    inventory_shortfall = st.slider(
        "📦 Inventory shortfall (fraction out-of-stock)",
        min_value=0.0, max_value=1.0, value=0.0, step=0.05,
    )

region_id = region_map[selected_state]

st.divider()
run_btn = st.button("▶ Run Simulation", type="primary")

if run_btn:
    with st.spinner("Running simulation…"):
        try:
            result = run_simulation(
                region_id=region_id,
                festival_next_week=festival_next_week,
                temperature_delta_c=temperature_delta,
                budget_multiplier=budget_multiplier,
                inventory_shortfall_pct=inventory_shortfall,
            )
        except Exception as e:
            st.error(f"Simulation error: {e}")
            st.stop()

    # ── KPI metrics ───────────────────────────────────────────────────────────
    conv  = result["predicted_conversion_rate"]
    rev   = result["predicted_revenue_index"]

    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Predicted Conversion Rate", f"{conv:.1%}")
    col_b.metric("Revenue Index", f"{rev:.1f} / 100")
    col_c.metric("Region", selected_state)

    # ── Gauge chart ───────────────────────────────────────────────────────────
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=conv * 100,
        title={"text": "Conversion Rate (%)"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "#FF6B35"},
            "steps": [
                {"range": [0, 30], "color": "#FFE5D9"},
                {"range": [30, 60], "color": "#FFB347"},
                {"range": [60, 100], "color": "#FF6B35"},
            ],
        },
    ))
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

    # ── Interpretation ────────────────────────────────────────────────────────
    st.subheader("📖 Interpretation")
    st.info(result.get("interpretation", "No interpretation available."))

    # ── Scenario summary ──────────────────────────────────────────────────────
    with st.expander("Scenario parameters used"):
        scenario = result.get("scenario", {})
        st.json(scenario)
