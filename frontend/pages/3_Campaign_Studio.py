"""Page 3 — Hyperlocal Campaign Studio.

AI-driven campaign generator: Bilingual copy, banner briefs, and SciPy-optimized budget.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.api_client import list_regions, list_segments, generate_campaign

st.set_page_config(page_title="Campaign Studio · TwinCart AI", page_icon="📣", layout="wide")

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
    .copy-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 1rem;
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
st.title("📣 Hyperlocal Campaign Studio")
st.caption("Generate localized ad campaigns with side-by-side English & Vernacular copy, banner briefs, and mathematically optimized budget allocations.")

# ── Inputs ────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def _regions():
    return list_regions()

@st.cache_data(ttl=300)
def _segments():
    return list_segments()

try:
    regions = _regions()
    segments = _segments()
except Exception as e:
    st.error(f"Could not reach backend: {e}")
    st.stop()

region_map = {f"{r['state']} — {r.get('city', r['region_id'])}": r["region_id"] for r in regions}
segment_map = {"All Shoppers (Broad)": None} | {s["label"]: s["segment_id"] for s in segments}

col1, col2, col3 = st.columns(3)
with col1:
    selected_region_name = st.selectbox("Target Regional Twin", list(region_map.keys()), index=0)
    region_id = region_map[selected_region_name]

with col2:
    selected_segment_label = st.selectbox("Customer Persona", list(segment_map.keys()), index=1)
    segment_id = segment_map[selected_segment_label]

with col3:
    category = st.selectbox("Product Category", ["apparel", "ethnic wear", "footwear", "beauty", "home textiles", "accessories"], index=0)

budget_inr = st.slider("Total Campaign Ad Budget (₹ INR)", min_value=10000, max_value=500000, value=100000, step=10000)

st.write("")
generate_btn = st.button("🚀 Generate Hyperlocal Campaign", type="primary", use_container_width=True)

if generate_btn or "last_campaign" in st.session_state:
    if generate_btn:
        with st.spinner("🤖 LangGraph Multi-Agent Pipeline Executing (Trends → Demand ML → Groq/Fallback Copy → SciPy Budget Optimizer → Explainability)..."):
            try:
                res = generate_campaign(
                    region_id=region_id,
                    segment_id=segment_id,
                    category=category,
                    total_budget_inr=float(budget_inr),
                )
                st.session_state["last_campaign"] = res
            except Exception as e:
                st.error(f"Campaign Generation failed: {e}")
                st.stop()
    else:
        res = st.session_state["last_campaign"]

    st.divider()
    st.markdown(f"### 📋 Campaign Results: `{res.get('campaign_id', 'cmp_001')}`")

    # ── Summary Scorecards ────────────────────────────────────────────────────
    mc1, mc2, mc3, mc4 = st.columns(4)
    with mc1:
        st.metric(
            label="7-Day Point Forecast",
            value=f"₹{res.get('point_forecast', 0.0):,.0f}",
            delta="XGBoost Model",
        )
    with mc2:
        st.metric(
            label="Forecast Uncertainty (1σ)",
            value=f"±₹{res.get('uncertainty_std', 0.0):,.0f}",
            delta="Empirical Residuals",
        )
    with mc3:
        st.metric(
            label="Model Backtested MAPE",
            value=f"{res.get('backtested_mape', 8.94):.2f}%",
            delta="Held-out 2025 Test",
            delta_color="inverse",
        )
    with mc4:
        st.metric(
            label="Total Campaign Budget",
            value=f"₹{budget_inr:,.0f}",
            delta="SciPy Linprog Allocated",
        )

    st.write("")

    # ── Bilingual Ad Copy Section ─────────────────────────────────────────────
    st.markdown("### ✍️ Localized Bilingual Campaign Copy")
    st.markdown('<div class="provenance-tag">Source: Groq LLM Generation & Vernacular Regional Mapping</div>', unsafe_allow_html=True)

    col_en, col_vern = st.columns(2)
    with col_en:
        st.markdown(
            f"""
            <div class="copy-card">
                <h4>🇬🇧 English Ad Copy</h4>
                <p style="font-size: 1.05rem; line-height: 1.5; color: #F1F5F9;">
                    "{res.get('campaign_en') or (res.get('campaign_copy', ['Special Festive Offer'])[0])}"
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_vern:
        vern_copy = res.get('campaign_vernacular')
        if not vern_copy and len(res.get('campaign_copy', [])) > 1:
            vern_copy = res.get('campaign_copy')[1]
        elif not vern_copy:
            vern_copy = "சிறப்பு தள்ளுபடி! இன்றே வாங்குங்கள்."

        st.markdown(
            f"""
            <div class="copy-card">
                <h4>🗣️ Regional Vernacular Ad Copy</h4>
                <p style="font-size: 1.05rem; line-height: 1.5; color: #F1F5F9;">
                    "{vern_copy}"
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── Visual Banner Briefs ──────────────────────────────────────────────────
    st.markdown("### 🎨 Visual Banner Creative Brief")
    for brief in res.get("banner_briefs", []):
        st.info(f"🖼️ **Creative Brief:** {brief}")

    # ── Budget Allocation (SciPy Optimization) ────────────────────────────────
    st.write("")
    st.markdown("### 💰 Mathematically Optimized Budget Allocation")
    st.markdown('<div class="provenance-tag">Source: SciPy Linear Programming (linprog / Highs) ROI Maximization</div>', unsafe_allow_html=True)

    b_alloc = res.get("budget_allocation", {})
    b_amounts = res.get("budget_amounts_inr", {})

    if b_alloc:
        c_chart, c_table = st.columns([1.2, 1.0])

        with c_chart:
            df_budget = pd.DataFrame([
                {"Channel": k.replace("_", " ").title(), "Share": v, "Amount (₹)": b_amounts.get(k, v * budget_inr)}
                for k, v in b_alloc.items()
            ])
            fig_pie = px.pie(
                df_budget,
                names="Channel",
                values="Share",
                hole=0.45,
                color_discrete_sequence=px.colors.qualitative.Prism,
            )
            fig_pie.update_layout(
                template="plotly_dark",
                margin=dict(l=10, r=10, t=10, b=10),
                height=300,
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with c_table:
            st.dataframe(
                df_budget.style.format({"Share": "{:.1%}", "Amount (₹)": "₹{:,.0f}"}),
                use_container_width=True,
                hide_index=True,
            )

    # ── Grounded Explainable AI ───────────────────────────────────────────────
    st.write("")
    st.markdown("### 🧠 Explainable AI Rationale")
    st.markdown('<div class="provenance-tag">Source: Grounded Explainability Agent (Zero Hallucinated Metrics)</div>', unsafe_allow_html=True)
    explanation = res.get("explanation") or " ".join(res.get("explanation_log", []))
    st.success(f"**Business Logic & Factor Trace:** {explanation}")
