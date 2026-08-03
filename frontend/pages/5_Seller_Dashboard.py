"""Page 5 — Seller Intelligence Dashboard."""
import streamlit as st
from utils.api_client import list_regions, list_segments, ask_seller_agent

st.set_page_config(page_title="Seller Dashboard · TwinCart AI", page_icon="🤝", layout="wide")
st.title("🤝 Seller Intelligence Dashboard")
st.caption(
    "Ask the AI agent anything about your market. "
    "Questions are answered using regional twin data and the 2026 festival calendar."
)

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

region_map  = {"(none)": None} | {r["state"]: r["region_id"] for r in regions}
segment_map = {"(none)": None} | {s["label"]: s["segment_id"] for s in segments}

# ── Context selectors ─────────────────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    region_label  = st.selectbox("Region context (optional)", list(region_map.keys()))
with col2:
    segment_label = st.selectbox("Segment context (optional)", list(segment_map.keys()))

region_id  = region_map[region_label]
segment_id = segment_map[segment_label]

# ── Question input ────────────────────────────────────────────────────────────
st.divider()
st.subheader("Ask a Question")

# Quick-start sample questions
sample_qs = [
    "Which products should I stock up on before Diwali in this region?",
    "What price point works best for this customer segment?",
    "When is the best time to run a sale in Kerala?",
    "What are the top catalog gaps I should fill right now?",
]
selected_sample = st.selectbox("💡 Quick-start questions", ["(type your own…)"] + sample_qs)
question_default = "" if selected_sample == "(type your own…)" else selected_sample
question = st.text_area("Your question", value=question_default, height=100,
                         placeholder="e.g. What products will sell best in Tamil Nadu this month?")

ask_btn = st.button("🔍 Ask Agent", type="primary", disabled=not question.strip())

if ask_btn and question.strip():
    with st.spinner("Consulting the Seller Intelligence Agent…"):
        try:
            result = ask_seller_agent(question.strip(), region_id, segment_id)
        except Exception as e:
            st.error(f"Agent error: {e}")
            st.stop()

    # ── Answer ────────────────────────────────────────────────────────────────
    st.subheader("💬 Answer")
    st.success(result.get("answer", "No answer returned."))

    col_a, col_b = st.columns(2)
    col_a.metric("Confidence", result.get("confidence", "—").capitalize())
    col_b.metric("From Cache", "Yes ✅" if result.get("from_cache") else "No (fresh)")

    # ── Supporting data ───────────────────────────────────────────────────────
    supporting = result.get("supporting_data") or {}
    if supporting:
        st.subheader("📌 Supporting Data")
        for key, val in supporting.items():
            st.markdown(f"**{key.replace('_', ' ').title()}:** {val}")

# ── Chat history (session state) ──────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

if ask_btn and question.strip() and "result" in dir():
    st.session_state["chat_history"].append({
        "q": question.strip(),
        "a": result.get("answer", ""),
    })

if st.session_state["chat_history"]:
    st.divider()
    st.subheader("📜 Session History")
    for entry in reversed(st.session_state["chat_history"]):
        with st.expander(f"Q: {entry['q'][:80]}…"):
            st.write(entry["a"])
