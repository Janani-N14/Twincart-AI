"""Page 3 — Hyperlocal Campaign Studio."""
import pandas as pd
import plotly.express as px
import streamlit as st
from utils.api_client import list_regions, list_segments, generate_campaign

st.set_page_config(page_title="Campaign Studio · TwinCart AI", page_icon="📣", layout="wide")
st.title("📣 Hyperlocal Campaign Studio")
st.caption("Generate AI-powered campaigns, banner briefs, and budget allocation for any region.")

# ── Inputs ─────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def _regions():
    return list_regions()

@st.cache_data(ttl=300)
def _segments():
    return list_segments()

try:
    regions  = _regions()
    segments = _segments()
except Exception as e:
    st.error(f"Could not reach backend: {e}")
    st.stop()

region_map  = {r["state"]: r["region_id"] for r in regions}
segment_map = {"(none)": None} | {s["label"]: s["segment_id"] for s in segments}

col1, col2 = st.columns(2)
with col1:
    selected_state = st.selectbox("Target Region", list(region_map.keys()))
with col2:
    selected_segment_label = st.selectbox("Customer Segment (optional)", list(segment_map.keys()))

region_id  = region_map[selected_state]
segment_id = segment_map[selected_segment_label]

st.divider()
generate_btn = st.button("🚀 Generate Campaign", type="primary", use_container_width=False)

if generate_btn:
    with st.spinner("Running TwinCart AI agent pipeline… (this may take 15–30 s on the free tier)"):
        try:
            result = generate_campaign(region_id, segment_id)
        except Exception as e:
            st.error(f"Pipeline error: {e}")
            st.stop()

    # ── Trends ────────────────────────────────────────────────────────────────
    st.subheader("📈 Detected Trends")
    trends = result.get("trends") or []
    if trends:
        cols = st.columns(len(trends))
        for c, trend in zip(cols, trends):
            c.success(f"✦ {trend}")
    else:
        st.info("No trends returned.")

    # ── Demand forecast ───────────────────────────────────────────────────────
    st.subheader("📊 Demand Forecast (next 30 days)")
    forecast = result.get("demand_forecast") or {}
    if forecast:
        df_forecast = pd.DataFrame(
            [{"Category": k, "Demand Index": v} for k, v in forecast.items()]
        ).sort_values("Demand Index", ascending=False)
        fig = px.bar(df_forecast, x="Category", y="Demand Index",
                     color="Demand Index", color_continuous_scale="Oranges",
                     range_y=[0, 100])
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No forecast data returned.")

    # ── Campaign copy ─────────────────────────────────────────────────────────
    st.subheader("📝 Campaign Copy")
    for line in (result.get("campaign_copy") or []):
        st.markdown(f"> {line}")

    # ── Banner briefs ─────────────────────────────────────────────────────────
    st.subheader("🖼️ Banner Briefs")
    for brief in (result.get("banner_briefs") or []):
        st.markdown(f"- {brief}")

    # ── Budget allocation ─────────────────────────────────────────────────────
    st.subheader("💰 Recommended Budget Allocation")
    budget = result.get("budget_allocation") or {}
    if budget:
        df_budget = pd.DataFrame(
            [{"Channel": k, "Fraction": v} for k, v in budget.items()]
        )
        fig2 = px.pie(df_budget, names="Channel", values="Fraction",
                      color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig2, use_container_width=True)

    # ── Catalog gaps ──────────────────────────────────────────────────────────
    gaps = result.get("catalog_gaps") or []
    if gaps:
        st.subheader("🔍 Catalog Gaps")
        for gap in gaps:
            st.warning(f"⚠ {gap}")

    # ── Weather signal ────────────────────────────────────────────────────────
    weather = result.get("weather_signal")
    if weather:
        st.subheader("🌤️ Weather & Festival Signal")
        st.info(weather)

    # ── Explanation ───────────────────────────────────────────────────────────
    explanation = result.get("explanation", "")
    if explanation:
        st.subheader("🧠 Why these recommendations?")
        st.info(explanation)
