import numpy as np
import plotly.express as px


def build_risk_heatmap():
    prep_range = np.arange(5, 100, 5)
    wait_range = np.arange(1, 60, 5)

    z_data = []

    for w in wait_range:
        row = []

        for p in prep_range:
            risk = (
                p / 100 * 0.4
                + w / 60 * 0.5
                + 10 / 50 * 0.1
            ) * 100

            row.append(min(risk, 100))

        z_data.append(row)

    fig_heatmap = px.imshow(
        z_data,
        x=prep_range,
        y=wait_range,
        labels={
            "x": "Kitchen Prep Time (mins)",
            "y": "Rider Wait Time (mins)",
            "color": "Risk Score %",
        },
        color_continuous_scale="RdYlGn_r",
        title="Risk Heatmap: Red Zone = High Cancellation Risk",
        aspect="auto",
    )

    fig_heatmap.update_layout(
        template="plotly_white",
        height=500,
    )

    return fig_heatmap


def build_feature_importance():
    features = [
        "Rider Wait Time",
        "KPT Duration",
        "Distance",
        "Order Hour",
        "Bill Subtotal",
        "Num Items",
    ]

    importance = [
        0.35,
        0.25,
        0.15,
        0.10,
        0.08,
        0.07,
    ]

    fig = px.bar(
        x=importance,
        y=features,
        orientation="h",
        color=importance,
        color_continuous_scale="Blues",
        labels={
            "x": "Importance Score",
            "y": "Feature",
        },
    )

    fig.update_layout(
        template="plotly_white",
        height=400,
    )

    return fig