"""Page 2 — Customer Segment Twins Explorer.

Interactive explorer of 5 localized consumer personas for Indian Tier-2/3 commerce.
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.api_client import list_segments, get_segment

st.set_page_config(page_title="Customer Segments · TwinCart AI", page_icon="👥", layout="wide")

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
    .persona-card {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 12px;
        padding: 1.2rem;
        height: 100%;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="disclosure-pill">Demo dataset — synthetic data</div>', unsafe_allow_html=True)
st.title("👥 Customer Segment Personas")
st.caption("5 localized consumer digital twin personas mapped across age brackets, price sensitivity, and cultural triggers.")

# ── Load Segments ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def _load_segments():
    return list_segments()

try:
    segments = _load_segments()
except Exception as e:
    st.error(f"Could not reach backend: {e}")
    st.stop()

# ── Persona Comparison Chart (Price Sensitivity) ──────────────────────────────
st.markdown("### 📊 Price Sensitivity & Budget Spectrum Across Personas")

seg_df = pd.DataFrame([
    {
        "Persona": s["label"],
        "Price Sensitivity (%)": s["price_sensitivity"] * 100.0,
        "Age Range": s["age_range"],
        "Budget Range": s.get("budget_range", s.get("income_bracket", "₹500 - ₹2,000")),
    }
    for s in segments
])

fig_sens = go.Figure(go.Bar(
    x=seg_df["Persona"],
    y=seg_df["Price Sensitivity (%)"],
    text=[f"{v:.0f}%" for v in seg_df["Price Sensitivity (%)"]],
    textposition="outside",
    marker_color=['#E63946', '#2A9D8F', '#F4A261', '#E76F51', '#457B9D'],
))
fig_sens.update_layout(
    template="plotly_dark",
    yaxis_title="Price Sensitivity (%)",
    yaxis_range=[0, 105],
    height=320,
    margin=dict(l=20, r=20, t=30, b=20),
)
st.plotly_chart(fig_sens, use_container_width=True)

st.divider()

# ── Detailed Persona Cards ────────────────────────────────────────────────────
st.markdown("### 🪪 Persona Deep-Dive")

seg_options = {s["label"]: s["segment_id"] for s in segments}
selected_label = st.selectbox("Select Persona", list(seg_options.keys()), index=0)
sid = seg_options[selected_label]
seg = get_segment(sid)

c1, c2, c3 = st.columns([1.2, 1.2, 1.6])

with c1:
    st.markdown(
        f"""
        <div class="persona-card">
            <h4>👤 {seg['label']}</h4>
            <p><b>Segment Code:</b> <code>{seg['segment_id']}</code></p>
            <p><b>Age Bracket:</b> {seg['age_range']} years</p>
            <p><b>Basket Budget:</b> {seg.get('budget_range', seg.get('income_bracket', '₹500 - ₹2,000'))}</p>
            <p><b>Price Sensitivity:</b> {seg['price_sensitivity']:.0%}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        f"""
        <div class="persona-card">
            <h4>🗣️ Language & Preferences</h4>
            <p><b>Preferred Language:</b> {seg.get('language', 'Bilingual / Vernacular')}</p>
            <p><b>Preferred Categories:</b></p>
            <ul>
                {''.join(f'<li>{cat}</li>' for cat in seg.get('preferred_categories', []))}
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c3:
    st.markdown(
        f"""
        <div class="persona-card">
            <h4>🎯 Purchase Triggers & Habits</h4>
            <p><b>Key Buying Catalysts:</b></p>
            <p>{seg.get('purchase_trigger', seg.get('platform_behaviour', 'Festival sales, peer trends, value bundles.'))}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
