import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier
from game.ui import fail_banner, lesson, level_header, win_banner
ACC_WIN = 0.80
FEATURES = ["wood_quality", "span", "wind", "age"]
def _bridges() -> pd.DataFrame:
    rng = np.random.default_rng(11)
    n = 160
    wood = rng.uniform(20, 100, n)
    span = rng.uniform(8, 90, n)
    wind = rng.uniform(2, 40, n)
    age = rng.uniform(1, 80, n)
    score = 0.045 * wood - 0.03 * span - 0.06 * wind - 0.025 * age + rng.normal(0, 0.35, n)
    safe = (score > 0.15).astype(int)
    return pd.DataFrame(
        {
            "bridge": [f"Span-{i+1}" for i in range(n)],
            "wood_quality": wood.round(1),
            "span": span.round(1),
            "wind": wind.round(1),
            "age": age.round(1),
            "safe": safe,
        }
    )
def render() -> None:
    level_header(
        4,
        "The chasm has many bridges. Some will hold; others crumble in the wind. "
        "Train a classifier on scouted crossings, then judge the untried spans.",
    )
    lesson(
        "Classification predicts a category (safe / unsafe) from features. "
        "Always test on bridges the model has never seen — training accuracy alone can lie."
    )
    df = _bridges()
    st.subheader("Scouted bridges")
    preview = df.copy()
    preview["safe"] = preview["safe"].map({1: "safe", 0: "unsafe"})
    st.dataframe(preview.head(12), use_container_width=True, hide_index=True)
    model_name = st.selectbox("Classifier", ["Logistic Regression", "Decision Tree"])
    depth = 3
    if model_name == "Decision Tree":
        depth = st.slider("Tree depth", 1, 8, 3)
    if st.button("Train and cross the test spans", type="primary"):
        x = df[FEATURES]
        y = df["safe"]
        x_train, x_test, y_train, y_test = train_test_split(
            x, y, test_size=0.30, random_state=4, stratify=y
        )
        if model_name == "Logistic Regression":
            scaler = StandardScaler()
            x_train_m = scaler.fit_transform(x_train)
            x_test_m = scaler.transform(x_test)
            model = LogisticRegression(max_iter=400)
        else:
            x_train_m, x_test_m = x_train, x_test
            model = DecisionTreeClassifier(max_depth=depth, random_state=4)
        model.fit(x_train_m, y_train)
        pred = model.predict(x_test_m)
        acc = float(accuracy_score(y_test, pred))
        cm = confusion_matrix(y_test, pred)
        ok = acc >= ACC_WIN
        if ok:
            msg = f"Your scouts named the safe spans with {acc:.0%} accuracy. The party crosses."
        else:
            msg = (
                f"Test accuracy {acc:.0%} is below {ACC_WIN:.0%}. "
                "Try logistic regression (a strong linear boundary fits this chasm) or a modest tree depth."
            )
        st.session_state.level_4_result = (ok, msg, cm, acc, len(y_test))
    if "level_4_result" in st.session_state:
        ok, msg, cm, acc, n_test = st.session_state.level_4_result
        fig = px.imshow(
            cm,
            text_auto=True,
            labels=dict(x="Predicted", y="Actual"),
            x=["unsafe", "safe"],
            y=["unsafe", "safe"],
            color_continuous_scale="YlGn",
            title="Confusion matrix (test bridges)",
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e8f0ea",
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig, use_container_width=True)
        c1, c2 = st.columns(2)
        c1.metric("Test accuracy", f"{acc:.0%}")
        c2.metric("Test bridges", f"{n_test}")
        if ok:
            win_banner(4, msg)
        else:
            fail_banner(msg)