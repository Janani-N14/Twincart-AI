"""TwinCart AI — Landing page / router.

Run with:  streamlit run streamlit_app.py   (from the frontend/ directory)
"""
import streamlit as st
from utils.api_client import health_check

st.set_page_config(
    page_title="TwinCart AI",
    page_icon="🪞",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🪞 TwinCart AI")
st.subheader("Hyperlocal Digital Twin & Agentic AI Platform for Bharat Commerce")

st.markdown(
    """
    TwinCart AI creates **Regional Digital Twins** and **Customer Segment Twins** for 15 Indian states,
    then runs a network of specialised AI agents to detect trends, forecast demand,
    generate hyperlocal campaigns, and run "what-if" simulations — all powered by **Groq** and **LangGraph**.

    Use the **sidebar** to navigate between modules.
    """
)

# ── Backend health indicator ──────────────────────────────────────────────────
st.divider()
col1, col2, col3 = st.columns([1, 1, 3])
with col1:
    if st.button("🔍 Check Backend", use_container_width=True):
        try:
            status = health_check()
            st.session_state["backend_ok"] = True
            st.session_state["backend_env"] = status.get("env", "unknown")
        except Exception as e:
            st.session_state["backend_ok"] = False
            st.session_state["backend_error"] = str(e)

with col2:
    if "backend_ok" in st.session_state:
        if st.session_state["backend_ok"]:
            st.success(f"Backend ✅  ({st.session_state.get('backend_env', '')})")
        else:
            st.error(f"Backend offline ❌\n{st.session_state.get('backend_error', '')}")

# ── Feature cards ─────────────────────────────────────────────────────────────
st.divider()
st.markdown("### What you can do")

c1, c2, c3, c4, c5 = st.columns(5)
c1.info("**🗺️ Regional Twins**\nExplore 15 state-level digital twins with festival & temperature data.")
c2.info("**👥 Customer Segments**\nBrowse the 4 customer segment twins: students, professionals, homemakers, budget shoppers.")
c3.info("**📣 Campaign Studio**\nGenerate hyperlocal AI campaign copy, banner briefs, and budget allocation.")
c4.info("**🔮 Simulation Engine**\nRun what-if scenarios: festival timing, budget changes, inventory shortfalls.")
c5.info("**🤝 Seller Dashboard**\nAsk the Seller Intelligence Agent free-form questions about your market.")

st.caption("TwinCart AI v1.0 · Powered by Groq + LangGraph · Final Year Project")
