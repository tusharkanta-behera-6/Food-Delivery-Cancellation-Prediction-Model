import joblib
import numpy as np
import pandas as pd
import streamlit as st

from utils.constants import (
    RISK_PROB_THRESHOLD,
    RULE_WAIT_THRESHOLD,
    RULE_KPT_THRESHOLD,
    WAIT_COST_PER_MIN,
    WAIT_SEARCH,
    DISCOUNT_SEARCH,
)


@st.cache_resource
def load_model(path="models/cancellation_model_rf.pkl"):
    return joblib.load(path)


def build_input_df(
    restaurant_name,
    subzone,
    city,
    distance_km,
    order_hour,
    num_items,
    bill_subtotal,
    kpt_duration,
    rider_wait_time,
):
    input_df = pd.DataFrame([{
        "Restaurant name": restaurant_name,
        "Subzone": subzone,
        "City": city,
        "Delivery": "Zomato Delivery",
        "Distance_km": float(distance_km),
        "Order_Hour": float(order_hour),
        "Order_Period": "Evening",
        "Day": "Tuesday",
        "Month": "September",
        "num_items": float(num_items),
        "Bill subtotal": float(bill_subtotal),
        "Packaging charges": 20.0,
        "Restaurant discount (Promo)": 0.0,
        "Restaurant discount (Flat offs, Freebies & others)": 0.0,
        "Gold discount": 0.0,
        "Brand pack discount": 0.0,
        "KPT duration (minutes)": float(kpt_duration),
        "Rider wait time (minutes)": float(rider_wait_time),
    }])

    return input_df


def predict(model, input_df, rider_wait_time, kpt_duration):
    prob = model.predict_proba(input_df)[0][1] * 100

    if (
        prob > RISK_PROB_THRESHOLD
        or (
            rider_wait_time > RULE_WAIT_THRESHOLD
            and kpt_duration > RULE_KPT_THRESHOLD
        )
    ):
        pred = 1
    else:
        pred = 0

    return prob, pred


def evaluate_intervention(
    model,
    base_df,
    discount,
    wait_red,
    kpt_duration,
    rider_wait_time,
):
    sim_df = base_df.copy()

    sim_df["Restaurant discount (Promo)"] = (
        sim_df["Restaurant discount (Promo)"] + discount
    )

    sim_df["Rider wait time (minutes)"] = np.maximum(
        0.0,
        sim_df["Rider wait time (minutes)"] - wait_red,
    )

    new_prob = model.predict_proba(sim_df)[0][1] * 100

    new_wait_value = float(
        np.maximum(0.0, rider_wait_time - wait_red)
    )

    if (
        new_prob > RISK_PROB_THRESHOLD
        or (
            new_wait_value > RULE_WAIT_THRESHOLD
            and kpt_duration > RULE_KPT_THRESHOLD
        )
    ):
        new_pred = 1
    else:
        new_pred = 0

    return new_prob, new_pred, new_wait_value


def prescriptive_search(
    model,
    base_df,
    kpt_duration,
    rider_wait_time,
):
    best_cost = float("inf")
    best_discount = 0
    best_wait_red = 0

    for wait_red in WAIT_SEARCH:
        for discount in DISCOUNT_SEARCH:

            new_prob, new_pred, new_wait_value = evaluate_intervention(
                model,
                base_df,
                discount,
                wait_red,
                kpt_duration,
                rider_wait_time,
            )

            if new_pred == 0:

                cost = discount + wait_red * WAIT_COST_PER_MIN

                if cost < best_cost:
                    best_cost = cost
                    best_discount = discount
                    best_wait_red = wait_red

    return {
        "discount": best_discount,
        "wait_red": best_wait_red,
        "cost": best_cost,
    }