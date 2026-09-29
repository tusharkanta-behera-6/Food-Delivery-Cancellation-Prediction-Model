import streamlit as st
from utils.charts import build_risk_heatmap, build_feature_importance


def _apply_dark_theme(fig):
    """Presentation-only theming. Chart data and logic are untouched."""
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Outfit, Inter, sans-serif", color="#c3d2ec", size=13),
        title_font_color="#eaf2ff",
        legend_font_color="#c3d2ec",
        margin=dict(l=20, r=20, t=50, b=20),
    )
    fig.update_xaxes(gridcolor="rgba(148,163,184,0.15)", linecolor="rgba(148,163,184,0.25)",
                     tickfont_color="#9fb3d9", title_font_color="#9fb3d9")
    fig.update_yaxes(gridcolor="rgba(148,163,184,0.15)", linecolor="rgba(148,163,184,0.25)",
                     tickfont_color="#9fb3d9", title_font_color="#9fb3d9")
    try:
        fig.update_layout(coloraxis_colorbar=dict(tickfont_color="#9fb3d9", title_font_color="#9fb3d9"))
    except Exception:
        pass
    return fig


def render():
    st.markdown('<h2 class="page-title">🧠 Explainable AI (XAI) Dashboard</h2>', unsafe_allow_html=True)
    st.markdown(
        '<p class="page-sub">Understanding why the model makes its decisions using clear, '
        'actionable visualizations.</p>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="glass-card"><p class="sidebar-label">Risk Heatmap · Prep Time vs Wait Time</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="page-sub" style="margin-top:0;">The <span class="hl-risk">red zone</span> indicates '
        'combinations of high prep time and high rider wait time that lead to maximum cancellation risk. '
        'The <span class="hl-safe">green zone</span> is safe.</p>',
        unsafe_allow_html=True
    )
    st.plotly_chart(_apply_dark_theme(build_risk_heatmap()), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="glass-card"><p class="sidebar-label">Top Factors Driving Order Cancellations</p>', unsafe_allow_html=True)
    st.plotly_chart(_apply_dark_theme(build_feature_importance()), use_container_width=True)

    st.markdown("""
    <div class="insight-list">
        <p><span class="insight-num">1</span><b>Rider Wait Time</b> is the #1 predictor. If a rider waits &gt;10 mins, cancellation risk spikes by 40%.</p>
        <p><span class="insight-num">2</span><b>Kitchen Prep Time (KPT)</b> is the second highest. Orders taking &gt;25 mins to prep are highly volatile.</p>
        <p><span class="insight-num">3</span><b>Distance</b> plays a minor role, but long distances combined with high prep times create a compounding risk.</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)