"""Page 5 — Seller Intelligence Advisor Dashboard.

Interactive natural-language advisor providing market pricing benchmarks,
regional demand outlooks, and catalog inventory strategies.
"""

import streamlit as st
import plotly.graph_objects as go

from utils.api_client import list_regions, list_segments, ask_seller_agent

st.set_page_config(page_title="Seller Dashboard · TwinCart AI", page_icon="🤝", layout="wide")

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
    .answer-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(46, 134, 171, 0.4);
        border-radius: 12px;
        padding: 1.5rem;
        margin-top: 1rem;
        font-size: 1.05rem;
        line-height: 1.6;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="disclosure-pill">Demo dataset — synthetic data</div>', unsafe_allow_html=True)
st.title("🤝 Seller Intelligence & Growth Advisor")
st.caption("Ask natural-language queries to receive empirical price benchmarks, demand forecasts, and regional stock strategies.")

# ── Load Context Data ─────────────────────────────────────────────────────────
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
segment_map = {s["label"]: s["segment_id"] for s in segments}

col1, col2, col3 = st.columns(3)
with col1:
    selected_region_name = st.selectbox("Target Market / District", list(region_map.keys()), index=0)
    region_id = region_map[selected_region_name]

with col2:
    selected_segment_label = st.selectbox("Customer Target Persona", list(segment_map.keys()), index=0)
    segment_id = segment_map[selected_segment_label]

with col3:
    category = st.selectbox("Product Category", ["apparel", "ethnic wear", "footwear", "beauty", "home textiles"], index=0)

st.divider()

# ── Question Input ────────────────────────────────────────────────────────────
st.markdown("### 💬 Ask the AI Seller Advisor")

sample_qs = [
    f"What is the demand forecast and optimal pricing strategy for {category} in this region?",
    f"Which price point maximizes sell-through for {selected_segment_label} without eroding margins?",
    "How much extra inventory buffer should I stock for upcoming regional festivals?",
    "What are the top catalog gaps and trending designs in this market right now?",
]
selected_sample = st.selectbox("💡 Quick-Start Questions", ["(Custom question...)"] + sample_qs)
question_default = "" if selected_sample == "(Custom question...)" else selected_sample

question = st.text_area(
    "Your Question",
    value=question_default,
    height=90,
    placeholder=f"e.g. What price should I sell cotton kurtas in Madurai for students?",
)

ask_btn = st.button("🔍 Get Grounded Advisor Insights", type="primary", use_container_width=True, disabled=not question.strip())

if ask_btn and question.strip():
    with st.spinner("Analyzing demand forecasts, category price percentiles, and regional calendars..."):
        try:
            result = ask_seller_agent(
                question=question.strip(),
                region_id=region_id,
                category=category,
                segment_id=segment_id,
            )
        except Exception as e:
            st.error(f"Advisor error: {e}")
            st.stop()

    st.write("")
    st.markdown("### 🎯 Strategic Recommendation")
    st.markdown('<div class="provenance-tag">Source: XGBoost Demand Model + Empirical Price Percentile Heuristics</div>', unsafe_allow_html=True)

    answer_text = result.get("answer", "No response.")
    st.markdown(
        f"""
        <div class="answer-card">
            {answer_text.replace(chr(10), '<br>')}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Market Price Percentiles Visualizer ────────────────────────────────────
    supp = result.get("supporting_data", {})
    if "median_price" in supp:
        st.write("")
        st.markdown("#### 🏷️ Empirical Category Price Benchmarks (₹ INR)")
        p25 = supp.get("p25_price", 520.0)
        p50 = supp.get("median_price", 699.0)
        p75 = supp.get("p75_price", 950.0)

        bc1, bc2, bc3, bc4 = st.columns(4)
        with bc1:
            st.metric("Entry Tier (25th Percentile)", f"₹{p25:,.0f}", delta="Value Volume")
        with bc2:
            st.metric("Market Median (50th Percentile)", f"₹{p50:,.0f}", delta="Sweet Spot", delta_color="normal")
        with bc3:
            st.metric("Premium Tier (75th Percentile)", f"₹{p75:,.0f}", delta="High Margin")
        with bc4:
            st.metric("Confidence", result.get("confidence", "high").title(), delta="Model Grounded")

    # ── Session History ───────────────────────────────────────────────────────
    if "seller_chat" not in st.session_state:
        st.session_state["seller_chat"] = []

    st.session_state["seller_chat"].append({
        "q": question.strip(),
        "a": answer_text,
    })

if st.session_state.get("seller_chat"):
    st.write("")
    st.divider()
    st.markdown("### 📜 Session History")
    for idx, item in enumerate(reversed(st.session_state["seller_chat"])):
        with st.expander(f"Q: {item['q']}", expanded=(idx == 0)):
            st.write(item["a"])
