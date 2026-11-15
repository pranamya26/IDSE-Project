import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from game.ui import fail_banner, lesson, level_header, win_banner
FEATURES = ["rainfall", "tree_glow", "monster_count", "crystal_power", "fog"]
def _forest() -> pd.DataFrame:
    rng = np.random.default_rng(21)
    n = 80
    rainfall = rng.normal(40, 10, n)
    tree_glow = 0.85 * rainfall + rng.normal(0, 2.2, n)
    fog = 0.35 * rainfall + rng.normal(12, 6, n)
    monster_count = rng.normal(15, 5, n) - 0.08 * rainfall
    crystal_power = rng.normal(50, 12, n)
    return pd.DataFrame(
        {
            "rainfall": np.clip(rainfall, 5, None).round(2),
            "tree_glow": np.clip(tree_glow, 0, None).round(2),
            "monster_count": np.clip(monster_count, 0, None).round(2),
            "crystal_power": np.clip(crystal_power, 0, None).round(2),
            "fog": np.clip(fog, 0, None).round(2),
        }
    )
def _strongest_pair(df: pd.DataFrame) -> tuple[str, str, float]:
    corr = df.corr(numeric_only=True).abs()
    best = (None, None, -1.0)
    cols = list(corr.columns)
    for i, a in enumerate(cols):
        for b in cols[i + 1 :]:
            val = float(corr.loc[a, b])
            if val > best[2]:
                best = (a, b, val)
    return best
def render() -> None:
    level_header(
        2,
        "The forest whispers in numbers. Some forces rise together; others wander alone. "
        "Find the strongest hidden relationship among the grove's measurements.",
    )
    lesson(
        "Correlation measures how two numeric features move together. "
        "A value near 1 or -1 is a strong linear relationship; near 0 means little linear link."
    )
    df = _forest()
    a_true, b_true, r_true = _strongest_pair(df)
    st.subheader("Grove measurements")
    st.dataframe(df.head(12), use_container_width=True, hide_index=True)
    corr = df.corr(numeric_only=True).round(3)
    fig = px.imshow(
        corr,
        text_auto=True,
        color_continuous_scale="YlGn",
        aspect="auto",
        title="Correlation heatmap",
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e8f0ea",
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig, use_container_width=True)
    c1, c2 = st.columns(2)
    with c1:
        feat_a = st.selectbox("First signal", FEATURES, index=0)
    with c2:
        feat_b = st.selectbox("Second signal", FEATURES, index=1)
    if feat_a != feat_b:
        scatter = px.scatter(
            df,
            x=feat_a,
            y=feat_b,
            title=f"{feat_a} vs {feat_b}",
        )
        scatter.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e8f0ea",
        )
        st.plotly_chart(scatter, use_container_width=True)
        observed = float(df[feat_a].corr(df[feat_b]))
        st.metric("Pearson correlation", f"{observed:.3f}")
    else:
        st.info("Pick two different signals.")
    if st.button("Declare this the hidden bond", type="primary"):
        if feat_a == feat_b:
            st.session_state.level_2_result = (
                False,
                "A feature does not reveal a relationship with itself. Choose two different signals.",
            )
        else:
            chosen = {feat_a, feat_b}
            truth = {a_true, b_true}
            r = abs(float(df[feat_a].corr(df[feat_b])))
            if chosen == truth:
                st.session_state.level_2_result = (
                    True,
                    f"{a_true} and {b_true} move together most strongly (|r| = {r_true:.2f}). "
                    "The grove's glow follows the rain.",
                )
            else:
                st.session_state.level_2_result = (
                    False,
                    f"|r| between {feat_a} and {feat_b} is {r:.2f}. "
                    "A stronger bond still hides in the forest (look for the darkest / brightest heatmap cell).",
                )
    if "level_2_result" in st.session_state:
        ok, msg = st.session_state.level_2_result
        if ok:
            win_banner(2, msg)
        else:
            fail_banner(msg)