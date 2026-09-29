import streamlit as st
import time
from datetime import datetime

from backend.model_service import build_input_df, predict, evaluate_intervention, prescriptive_search
from utils.constants import RESTAURANTS, CITIES


def _history_table_html(log):
    rows = []
    for r in log:
        pill = "pill-risk" if r["Status"] == "HIGH RISK" else "pill-safe"
        rows.append(
            "<tr>"
            "<td>" + str(r["Time"]) + "</td>"
            "<td>" + str(r["Restaurant"]) + "</td>"
            "<td>" + str(r["Prep Time"]) + "</td>"
            "<td>" + str(r["Wait Time"]) + "</td>"
            "<td>" + str(r["Probability"]) + "</td>"
            '<td><span class="pill ' + pill + '">' + str(r["Status"]) + "</span></td>"
            "</tr>"
        )
    return (
        '<div class="table-wrap"><table class="enterprise-table"><thead><tr>'
        "<th>Time</th><th>Restaurant</th><th>Prep Time</th><th>Wait Time</th>"
        "<th>Probability</th><th>Status</th>"
        "</tr></thead><tbody>" + "".join(rows) + "</tbody></table></div>"
    )


def render(model):
    # ---- session init ----
    if 'init_done' not in st.session_state:
        st.session_state.init_done = False
    if 'sim_done' not in st.session_state:
        st.session_state.sim_done = False
    if 'prediction_log' not in st.session_state:
        st.session_state.prediction_log = []

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="glass-card"><div class="section-title">📍 Location & Restaurant</div>', unsafe_allow_html=True)
        restaurant_name = st.selectbox("🏪 Restaurant Name", RESTAURANTS)
        city = st.selectbox("🌆 City", CITIES)
        subzone = st.text_input("🗺️ Subzone / Area", "Sector 4")
        distance_km = st.number_input("📏 Distance (km)", min_value=0.0, max_value=100.0, value=45.0, step=0.1)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="glass-card"><div class="section-title">⏱️ Operational Metrics</div>', unsafe_allow_html=True)
        kpt_duration = st.number_input("👨‍🍳 Kitchen Prep Time (mins)", 0.0, 180.0, value=90.0, step=1.0)
        rider_wait_time = st.number_input("⏳ Rider Wait Time (mins)", 0.0, 120.0, value=55.0, step=1.0)
        order_hour = st.number_input("🕒 Order Hour (0-23)", min_value=0, max_value=23, value=3, step=1)
        num_items = st.number_input("🍟 Number of Items", 1, 50, value=20)
        bill_subtotal = st.number_input("💵 Bill Subtotal (₹)", min_value=0.0, value=3000.0, step=50.0)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_left, col_mid, col_right = st.columns([1, 2, 1])
    with col_mid:
        predict_clicked = st.button("🚀 Run Initial Prediction", type="primary", use_container_width=True)

    # ---- initial prediction (logic untouched, backend only) ----
    if predict_clicked:
        with st.spinner("🤖 AI is analyzing order patterns..."):
            time.sleep(1.5)
            input_df = build_input_df(restaurant_name, subzone, city, distance_km, order_hour,
                                      num_items, bill_subtotal, kpt_duration, rider_wait_time)
            prob, pred = predict(model, input_df, rider_wait_time, kpt_duration)

            st.session_state.init_done = True
            st.session_state.prob = prob
            st.session_state.pred = pred
            st.session_state.input_df = input_df
            st.session_state.bill_subtotal = bill_subtotal
            st.session_state.kpt_duration = kpt_duration
            st.session_state.rider_wait_time = rider_wait_time
            st.session_state.sim_done = False

            st.session_state.history.append({
                'time': datetime.now().strftime("%H:%M"),
                'rest': restaurant_name,
                'status': pred
            })
            st.session_state.prediction_log.insert(0, {
                "Time": datetime.now().strftime("%H:%M:%S"),
                "Restaurant": restaurant_name,
                "Prep Time": kpt_duration,
                "Wait Time": rider_wait_time,
                "Probability": f"{prob:.1f}%",
                "Status": "HIGH RISK" if pred == 1 else "LOW RISK"
            })

            if pred == 1:
                suggestion = prescriptive_search(model, input_df, kpt_duration, rider_wait_time)
                st.session_state.ai_discount = suggestion['discount']
                st.session_state.ai_wait_red = suggestion['wait_red']
                st.session_state.ai_cost = suggestion['cost']

    # ---- results ----
    if st.session_state.init_done:
        prob = st.session_state.prob
        pred = st.session_state.pred

        st.markdown("<br>", unsafe_allow_html=True)
        res_col1, res_col2 = st.columns([1, 1])

        with res_col1:
            if pred == 1:
                risk_text = f"{prob:.1f}%" if prob > 0 else "CRITICAL (Business Rule Override)"
                st.markdown(f"""
                <div class="result-card result-danger">
                    <span class="pulse-badge">LIVE RISK ALERT</span>
                    <h2 class="result-title" style="margin-top:14px;">🔴 HIGH RISK</h2>
                    <p class="result-sub">This order is highly likely to be CANCELLED.</p>
                    <p class="result-prob">Probability: {risk_text}</p>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="result-card result-success">
                    <h2 class="result-title">🟢 LOW RISK</h2>
                    <p class="result-sub">This order is unlikely to be cancelled.</p>
                    <p class="result-prob">Probability: {prob:.1f}%</p>
                </div>""", unsafe_allow_html=True)

        with res_col2:
            if pred == 1:
                reco_body = ('<div class="reco-body reco-body-warn">⚠️ <b>Action Required:</b> '
                             'High risk of cancellation detected! Use the prescriptive engine below '
                             'to save this order.</div>')
            else:
                reco_body = ('<div class="reco-body reco-body-safe">✅ <b>All Clear:</b> '
                             'Order parameters are healthy. Proceed with standard dispatch.</div>')
            st.markdown(
                '<div class="reco-card"><h3 class="reco-title">💡 Operational Recommendation</h3>'
                + reco_body + '</div>',
                unsafe_allow_html=True
            )

        # ---- AI auto-suggestion ----
        if pred == 1:
            ai_disc = st.session_state.ai_discount
            ai_wait = st.session_state.ai_wait_red
            ai_cost = st.session_state.ai_cost
            bill_val = st.session_state.bill_subtotal
            st.markdown(f"""
            <div class="ai-glow"><div class="ai-suggestion-box">
                <h3 class="ai-title">🤖 AI Auto-Suggestion: Cheapest Way to Save This Order</h3>
                <p>To bring the risk down to a safe level and save this <b>₹{bill_val}</b> order,
                the AI recommends the following minimum intervention:</p>
                <ul>
                    <li>💰 <b>Apply a Discount Coupon:</b> ₹{ai_disc}</li>
                    <li>⏱️ <b>Reduce Rider Wait Time by:</b> {ai_wait} minutes</li>
                </ul>
                <p style="margin-top:14px; font-size:1.15rem;">Total Intervention Cost:
                <span class="cost-highlight">₹{ai_cost}</span></p>
            </div></div>""", unsafe_allow_html=True)

            # ---- manual simulator ----
            st.markdown('<div class="sim-panel">', unsafe_allow_html=True)
            st.markdown('<h3 class="sim-title">🛠️ Manual Intervention Simulator</h3>', unsafe_allow_html=True)
            st.markdown('<p class="sim-sub">Want to test a different strategy? Adjust the values below.</p>', unsafe_allow_html=True)

            sim_col1, sim_col2 = st.columns(2)
            with sim_col1:
                sim_discount = st.number_input("💰 Add Discount Coupon (₹)", 0, 500, ai_disc, step=10)
            with sim_col2:
                sim_wait_reduction = st.number_input("⏱️ Reduce Rider Wait Time (mins)", 0, 60, ai_wait, step=1)

            recalc_clicked = st.button("🔄 Recalculate Risk with Manual Intervention",
                                       type="primary", use_container_width=True)

            if recalc_clicked:
                new_prob, new_pred, _ = evaluate_intervention(
                    model,
                    st.session_state.input_df,
                    sim_discount,
                    sim_wait_reduction,
                    st.session_state.kpt_duration,
                    st.session_state.rider_wait_time
                )
                st.session_state.sim_done = True
                st.session_state.new_prob = new_prob
                st.session_state.new_pred = new_pred
                st.session_state.sim_discount = sim_discount

            if st.session_state.sim_done:
                new_prob = st.session_state.new_prob
                new_pred = st.session_state.new_pred
                sim_discount = st.session_state.sim_discount
                bill_subtotal = st.session_state.bill_subtotal

                st.markdown(
                    f'<div class="sim-result">📉 New Risk Probability: <b>{new_prob:.1f}%</b> '
                    f'<span class="muted">(Previously {prob:.1f}%)</span></div>',
                    unsafe_allow_html=True
                )

                if new_pred == 0:
                    net_profit_saved = bill_subtotal - sim_discount
                    st.markdown(f"""
                    <div class="success-box">🎉 INTERVENTION SUCCESSFUL! The order is now predicted to be completed.</div>
                    <div class="roi-box">
                        <h4 class="roi-title">💰 Business Value (ROI) of this Intervention</h4>
                        <ul>
                            <li><b>Revenue Saved:</b> ₹{bill_subtotal:.2f}</li>
                            <li><b>Cost of Discount:</b> −₹{sim_discount:.2f}</li>
                            <li><b>Net Profit Saved:</b> <span class="roi-net">₹{net_profit_saved:.2f}</span></li>
                        </ul>
                    </div>""", unsafe_allow_html=True)
                else:
                    st.markdown(
                        '<div class="warn-box">⚠️ Risk reduced, but still high. '
                        'Try a larger discount or reducing prep time further.</div>',
                        unsafe_allow_html=True
                    )
            st.markdown('</div>', unsafe_allow_html=True)

    # ---- history ----
    st.markdown(
        '<h2 class="history-title">📜 Session Prediction History</h2>'
        '<p class="history-sub">Recent cancellation-risk predictions from this session</p>',
        unsafe_allow_html=True
    )
    if len(st.session_state.prediction_log) == 0:
        st.markdown("""
        <div class="empty-state">
            <p class="empty-icon">📊</p>
            <p class="empty-title">No predictions yet</p>
            <p class="empty-sub">Run an initial prediction to start building your session history.</p>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(_history_table_html(st.session_state.prediction_log), unsafe_allow_html=True)