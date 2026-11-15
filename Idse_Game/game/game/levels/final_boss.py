import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier
from game.ui import fail_banner, lesson, level_header, win_banner
F1_WIN = 0.80
ALL_FEATURES = [
    "corruption_signal",
    "citizen_trust",
    "mana_flow",
    "market_noise",
    "cloud_static",
]
def _kingdom() -> pd.DataFrame:
    rng = np.random.default_rng(99)
    n = 240
    corruption = rng.normal(0.4, 0.25, n)
    trust = rng.normal(0.55, 0.2, n)
    mana = rng.normal(0.5, 0.22, n)
    noise = rng.normal(0, 1, n)
    static = rng.normal(0, 1, n)
    score = 2.8 * corruption - 2.1 * trust - 1.4 * mana + rng.normal(0, 0.22, n)
    corrupted = (score > 0.15).astype(int)
    return pd.DataFrame(
        {
            "region": [f"Hex-{i+1}" for i in range(n)],
            "corruption_signal": np.clip(corruption, 0, 1).round(3),
            "citizen_trust": np.clip(trust, 0, 1).round(3),
            "mana_flow": np.clip(mana, 0, 1).round(3),
            "market_noise": noise.round(3),
            "cloud_static": static.round(3),
            "corrupted": corrupted,
        }
    )
def render() -> None:
    level_header(
        6,
        "The evil AI occupies the last hexes of the Data Kingdom. "
        "Build a model that flags corrupted regions on unseen land — measured by F1, not vanity training scores.",
    )
    lesson(
        "Model evaluation uses held-out data and several metrics. Accuracy can hide a weak minority class; "
        "precision, recall, and F1 tell you how well corrupted hexes are actually caught."
    )
    df = _kingdom()
    preview = df.copy()
    preview["corrupted"] = preview["corrupted"].map({1: "corrupted", 0: "clear"})
    st.subheader("Kingdom survey")
    st.dataframe(preview.head(12), use_container_width=True, hide_index=True)
    features = st.multiselect(
        "Features for the final model",
        ALL_FEATURES,
        default=["corruption_signal", "citizen_trust", "mana_flow"],
    )
    model_name = st.selectbox(
        "Algorithm",
        ["Logistic Regression", "Decision Tree", "Random Forest", "k-Nearest Neighbors"],
    )
    scale = st.checkbox("Scale features", value=True)
    extra = {}
    if model_name == "Decision Tree":
        extra["depth"] = st.slider("max_depth", 1, 12, 4)
    if model_name == "Random Forest":
        extra["depth"] = st.slider("max_depth", 2, 12, 5)
        extra["trees"] = st.slider("n_estimators", 20, 200, 80, step=10)
    if model_name == "k-Nearest Neighbors":
        extra["k"] = st.slider("k neighbors", 1, 15, 5)
    if st.button("Challenge the AI", type="primary"):
        if len(features) < 2:
            st.session_state.level_6_result = (
                False,
                "Choose at least two features. A single signal is too easy for the AI to scramble.",
                None,
            )
        else:
            x = df[features]
            y = df["corrupted"]
            x_train, x_test, y_train, y_test = train_test_split(
                x, y, test_size=0.30, random_state=3, stratify=y
            )
            if scale:
                scaler = StandardScaler()
                x_train_m = scaler.fit_transform(x_train)
                x_test_m = scaler.transform(x_test)
            else:
                x_train_m, x_test_m = x_train, x_test
            if model_name == "Logistic Regression":
                model = LogisticRegression(max_iter=500)
            elif model_name == "Decision Tree":
                model = DecisionTreeClassifier(max_depth=extra["depth"], random_state=3)
            elif model_name == "Random Forest":
                model = RandomForestClassifier(
                    n_estimators=extra["trees"],
                    max_depth=extra["depth"],
                    random_state=3,
                )
            else:
                model = KNeighborsClassifier(n_neighbors=extra["k"])
            model.fit(x_train_m, y_train)
            pred = model.predict(x_test_m)
            acc = float(accuracy_score(y_test, pred))
            prec = float(precision_score(y_test, pred, zero_division=0))
            rec = float(recall_score(y_test, pred, zero_division=0))
            f1 = float(f1_score(y_test, pred, zero_division=0))
            cm = confusion_matrix(y_test, pred)
            ok = f1 >= F1_WIN
            if ok:
                msg = f"F1 {f1:.0%} on unseen hexes. The AI's hold breaks. The Data Kingdom is yours to restore."
            else:
                msg = (
                    f"F1 {f1:.0%} is below the {F1_WIN:.0%} relic threshold. "
                    "Prefer corruption_signal, citizen_trust, and mana_flow — market_noise and cloud_static are decoys."
                )
            st.session_state.level_6_result = (ok, msg, (acc, prec, rec, f1, cm))
    if "level_6_result" in st.session_state:
        ok, msg, payload = st.session_state.level_6_result
        if payload:
            acc, prec, rec, f1, cm = payload
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Accuracy", f"{acc:.0%}")
            m2.metric("Precision", f"{prec:.0%}")
            m3.metric("Recall", f"{rec:.0%}")
            m4.metric("F1", f"{f1:.0%}")
            fig = px.imshow(
                cm,
                text_auto=True,
                labels=dict(x="Predicted", y="Actual"),
                x=["clear", "corrupted"],
                y=["clear", "corrupted"],
                color_continuous_scale="YlGn",
                title="Confusion matrix (held-out hexes)",
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#e8f0ea",
                coloraxis_showscale=False,
            )
            st.plotly_chart(fig, use_container_width=True)
        if ok:
            win_banner(6, msg)
        else:
            fail_banner(msg)