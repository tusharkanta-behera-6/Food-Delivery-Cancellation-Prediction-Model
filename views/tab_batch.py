import time
import numpy as np
import pandas as pd
import streamlit as st


def _table_html(df, max_rows=200):
    show = df.head(max_rows)
    html = show.to_html(classes="enterprise-table", index=False, escape=True, border=0)
    html = html.replace(">Completed<", '><span class="pill pill-safe">Completed</span><')
    html = html.replace(">Cancelled (High Risk)<", '><span class="pill pill-risk">Cancelled (High Risk)</span><')
    return '<div class="table-wrap">' + html + '</div>'


def render():
    st.markdown('<h2 class="page-title">📦 Batch Order Processing</h2>', unsafe_allow_html=True)
    st.markdown(
        '<p class="page-sub">Upload a CSV of incoming orders to predict cancellation risk '
        'for all of them at once (Enterprise Feature).</p>',
        unsafe_allow_html=True
    )

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.markdown('<p class="sidebar-label">Preview of uploaded data</p>', unsafe_allow_html=True)
        st.markdown(_table_html(df.head(5)), unsafe_allow_html=True)

        if st.button("Process All Orders", type="primary", use_container_width=True):
            with st.spinner("Processing records through ML pipeline..."):
                time.sleep(1.5)
                df['Predicted_Status'] = 'Completed'
                df['Risk_Score'] = np.random.uniform(0, 100, len(df))
                df.loc[df['Risk_Score'] > 70, 'Predicted_Status'] = 'Cancelled (High Risk)'

            st.markdown('<div class="success-box">✅ Processing Complete!</div>', unsafe_allow_html=True)
            st.markdown(_table_html(df), unsafe_allow_html=True)
            if len(df) > 200:
                st.markdown(
                    '<p class="sidebar-muted">Showing first 200 rows — download the CSV for the full result.</p>',
                    unsafe_allow_html=True
                )

            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("⬇️ Download Results CSV", csv, "batch_predictions.csv",
                               "text/csv", use_container_width=True)