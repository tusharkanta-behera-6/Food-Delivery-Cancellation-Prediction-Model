import streamlit as st


def render_sidebar():
    with st.sidebar:
        st.markdown('<div class="sidebar-brand">🛒 <span>Delivery AI Ops</span></div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

        st.markdown('<p class="sidebar-label">Model Telemetry</p>', unsafe_allow_html=True)
        st.metric("Model Version", "v4.0.0 (Prescriptive AI)")
        st.metric("Training Data", "21,321 Orders")
        st.metric("Accuracy", "99.46%")
        st.metric("Precision", "100.0%")
        st.metric("Recall", "37.84%")

        st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
        st.markdown('<p class="sidebar-label">Quick History</p>', unsafe_allow_html=True)

        if 'history' not in st.session_state:
            st.session_state.history = []

        if st.button("🗑️ Clear All History", use_container_width=True):
            st.session_state.history = []
            if 'prediction_log' in st.session_state:
                st.session_state.prediction_log = []

        if len(st.session_state.history) == 0:
            st.markdown('<p class="sidebar-muted">No recent predictions.</p>', unsafe_allow_html=True)
        else:
            for entry in reversed(st.session_state.history[-5:]):
                if entry['status'] == 1:
                    line = f'<p class="sidebar-history hist-risk">🔴 {entry["time"]} · {entry["rest"]} · High Risk</p>'
                else:
                    line = f'<p class="sidebar-history hist-safe">🟢 {entry["time"]} · {entry["rest"]} · Safe</p>'
                st.markdown(line, unsafe_allow_html=True)