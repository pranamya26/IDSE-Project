import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from game.ui import fail_banner, lesson, level_header, win_banner
TEST_MIN = 0.75
GAP_MAX = 0.13
def _castle() -> tuple[pd.DataFrame, np.ndarray]:
    rng = np.random.default_rng(5)
    n = 220
    x1 = rng.normal(0, 1, n)
    x2 = rng.normal(0, 1, n)
    x3 = rng.normal(0, 1, n)
    noise = rng.normal(0, 1.15, n)
    # Smooth-ish decision: a shallow tree can capture it; deep trees chase noise.
    logit = 1.6 * x1 - 1.1 * x2 + 0.4 * (x1 * x2) + noise
    y = (logit > 0).astype(int)
    df = pd.DataFrame({"ward_sigil": x1, "echo_hum": x2, "dust_mote": x3})
    return df, y
def _curve(x_train, x_test, y_train, y_test) -> pd.DataFrame:
    rows = []
    for depth in range(1, 16):
        model = DecisionTreeClassifier(max_depth=depth, random_state=0)
        model.fit(x_train, y_train)
        rows.append(
            {
                "max_depth": depth,
                "train": accuracy_score(y_train, model.predict(x_train)),
                "test": accuracy_score(y_test, model.predict(x_test)),
            }
        )
    return pd.DataFrame(rows)
def render() -> None:
    level_header(
        5,
        "The castle rewards models that memorize every cobblestone — and then collapses on new rooms. "
        "Choose a tree depth that still works on halls the model has never walked.",
    )
    lesson(
        "Overfitting means training score looks heroic while test score falls. "
        "Underfitting means both scores stay weak. A useful model generalizes: high test accuracy and a small train–test gap."
    )
    x, y = _castle()
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.35, random_state=8, stratify=y
    )
    curve = _curve(x_train, x_test, y_train, y_test)
    depth = st.slider("Decision tree max_depth", 1, 15, 11)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=curve["max_depth"], y=curve["train"], name="Train accuracy", mode="lines+markers"))
    fig.add_trace(go.Scatter(x=curve["max_depth"], y=curve["test"], name="Test accuracy", mode="lines+markers"))
    fig.add_vline(x=depth, line_dash="dash", line_color="#c9a24a")
    fig.update_layout(
        title="Train vs test as the tree grows",
        xaxis_title="max_depth",
        yaxis_title="accuracy",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e8f0ea",
        legend=dict(orientation="h"),
        yaxis=dict(range=[0.45, 1.02]),
    )
    st.plotly_chart(fig, use_container_width=True)
    row = curve.loc[curve["max_depth"] == depth].iloc[0]
    train_acc, test_acc = float(row["train"]), float(row["test"])
    gap = train_acc - test_acc
    if test_acc < 0.70 and train_acc < 0.80:
        badge = "Underfit"
    elif gap > GAP_MAX:
        badge = "Overfit"
    else:
        badge = "Good fit"
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Train accuracy", f"{train_acc:.0%}")
    c2.metric("Test accuracy", f"{test_acc:.0%}")
    c3.metric("Train − test gap", f"{gap:.0%}")
    c4.metric("Verdict", badge)
    if st.button("Seal this model into the castle", type="primary"):
        if badge == "Good fit" and test_acc >= TEST_MIN and gap <= GAP_MAX:
            st.session_state.level_5_result = (
                True,
                f"Depth {depth} generalizes (test {test_acc:.0%}, gap {gap:.0%}). New halls stay standing.",
            )
        elif badge == "Overfit":
            st.session_state.level_5_result = (
                False,
                f"Depth {depth} memorizes the training stones (gap {gap:.0%}). "
                "Lower max_depth until the gold and green curves stay close.",
            )
        elif badge == "Underfit":
            st.session_state.level_5_result = (
                False,
                f"Depth {depth} is too simple (test {test_acc:.0%}). Grow the tree a little so it can learn the ward pattern.",
            )
        else:
            st.session_state.level_5_result = (
                False,
                f"Close, but test accuracy {test_acc:.0%} is still under {TEST_MIN:.0%} "
                f"or the gap {gap:.0%} exceeds {GAP_MAX:.0%}. Aim for a modest depth.",
            )
    if "level_5_result" in st.session_state:
        ok, msg = st.session_state.level_5_result
        if ok:
            win_banner(5, msg)
        else:
            fail_banner(msg)