import os
import streamlit as st

from backend.model_service import load_model
from views import sidebar as sidebar_view
from views import tab_single, tab_batch, tab_insights

st.set_page_config(
    page_title="Food Delivery AI | Cancellation Predictor",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---- Load enterprise dark theme ----
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSS_PATH = os.path.join(BASE_DIR, "styles", "style.css")
with open(CSS_PATH, "r", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ---- Sidebar ----
sidebar_view.render_sidebar()

# ---- Hero ----
st.markdown("""
<div class="hero-container">
    <h1 class="hero-title">🍔 Food Delivery Cancellation Predictor</h1>
    <p class="hero-subtitle">Real-time operational risk assessment and prescriptive analytics for delivery logistics</p>
</div>
""", unsafe_allow_html=True)

# ---- Model (service layer) ----
try:
    model = load_model()
except Exception:
    st.error("⚠️ Model not found. Please run the training script first.")
    st.stop()

# ---- Tabs ----
tab_s, tab_b, tab_i = st.tabs([
    "🎯 Single Order & AI Suggestions",
    "📦 Batch CSV Processing",
    "🧠 Model Insights (XAI)"
])

with tab_s:
    tab_single.render(model)
with tab_b:
    tab_batch.render()
with tab_i:
    tab_insights.render()