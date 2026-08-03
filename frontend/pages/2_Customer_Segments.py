"""Page 2 — Customer Segment Twins explorer."""
import pandas as pd
import streamlit as st
from utils.api_client import list_segments, get_segment

st.set_page_config(page_title="Customer Segments · TwinCart AI", page_icon="👥", layout="wide")
st.title("👥 Customer Segment Twins")
st.caption("Four canonical customer segments modelled as digital twins.")

@st.cache_data(ttl=300)
def _load_segments():
    return list_segments()

try:
    segments = _load_segments()
except Exception as e:
    st.error(f"Could not reach backend: {e}")
    st.stop()

# ── Summary cards ─────────────────────────────────────────────────────────────
cols = st.columns(len(segments))
for col, seg in zip(cols, segments):
    with col:
        st.markdown(f"### {seg['label']}")
        st.metric("Price Sensitivity", f"{seg['price_sensitivity']:.0%}")
        st.markdown(f"**Age:** {seg['age_range']}")
        st.markdown(f"**Income:** {seg['income_bracket']}")

# ── Detail view ───────────────────────────────────────────────────────────────
st.divider()
st.subheader("Segment Detail")
seg_options = {s["label"]: s["segment_id"] for s in segments}
selected_label = st.selectbox("Select a segment", list(seg_options.keys()))

if selected_label:
    sid = seg_options[selected_label]
    try:
        seg = get_segment(sid)
    except Exception as e:
        st.error(str(e))
        st.stop()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Segment ID:** `{seg['segment_id']}`")
        st.markdown(f"**Age Range:** {seg['age_range']}")
        st.markdown(f"**Income Bracket:** {seg['income_bracket']}")
        st.markdown(f"**Price Sensitivity:** {seg['price_sensitivity']:.0%}")
    with col2:
        st.markdown("**Preferred Categories**")
        for cat in seg["preferred_categories"]:
            st.write(f"• {cat}")
        st.markdown("**Platform Behaviour**")
        st.info(seg["platform_behaviour"])

    if seg.get("region_ids"):
        st.markdown("**Key Regions**")
        st.write(", ".join(seg["region_ids"]))
