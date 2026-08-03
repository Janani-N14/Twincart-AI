"""Page 1 — Regional Digital Twins explorer."""
import pandas as pd
import streamlit as st
from utils.api_client import list_regions, get_region

st.set_page_config(page_title="Regional Twins · TwinCart AI", page_icon="🗺️", layout="wide")
st.title("🗺️ Regional Digital Twins")
st.caption("Browse all 15 state-level digital twins — live data from the TwinCart AI backend.")

# ── Load all twins ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def _load_regions():
    return list_regions()

try:
    regions = _load_regions()
except Exception as e:
    st.error(f"Could not reach backend: {e}")
    st.stop()

# ── Summary table ─────────────────────────────────────────────────────────────
df = pd.DataFrame([
    {
        "Region ID": r["region_id"],
        "State": r["state"],
        "Languages": ", ".join(r["languages"]),
        "Top Categories": ", ".join(r["top_categories"][:2]),
        "Price Sensitivity": r["price_sensitivity"],
        "Avg Temp (°C)": r.get("avg_temperature_c", "—"),
    }
    for r in regions
])

st.dataframe(df, use_container_width=True, hide_index=True)

# ── Detail view ───────────────────────────────────────────────────────────────
st.divider()
st.subheader("Twin Detail")
region_options = {r["state"]: r["region_id"] for r in regions}
selected_state = st.selectbox("Select a state", list(region_options.keys()))

if selected_state:
    rid = region_options[selected_state]
    try:
        twin = get_region(rid)
    except Exception as e:
        st.error(str(e))
        st.stop()

    col1, col2, col3 = st.columns(3)
    col1.metric("Region ID", twin["region_id"])
    col2.metric("Price Sensitivity", f"{twin['price_sensitivity']:.0%}")
    col3.metric("Avg Temperature", f"{twin.get('avg_temperature_c', '—')} °C")

    col4, col5 = st.columns(2)
    with col4:
        st.markdown("**Languages**")
        st.write(", ".join(twin["languages"]))
        st.markdown("**Top Categories**")
        for cat in twin["top_categories"]:
            st.write(f"• {cat}")
    with col5:
        st.markdown("**Active Festivals**")
        for fest in twin.get("active_festivals", []):
            st.write(f"🎉 {fest}")
