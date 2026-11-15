import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
from sklearn.preprocessing import StandardScaler
from game.ui import fail_banner, lesson, level_header, win_banner
FEATURES = ["speed", "strength", "size"]
ARI_WIN = 0.70
def _monsters() -> pd.DataFrame:
    rng = np.random.default_rng(42)
    tribes = {
        "Swiftling": {"speed": (88, 6), "strength": (28, 6), "size": (18, 4)},
        "Ironhide": {"speed": (32, 6), "strength": (86, 6), "size": (78, 5)},
        "Mystic": {"speed": (58, 7), "strength": (55, 7), "size": (48, 6)},
    }
    rows = []
    idx = 0
    for tribe, stats in tribes.items():
        n = 24
        speed = rng.normal(*stats["speed"], n)
        strength = rng.normal(*stats["strength"], n)
        size = rng.normal(*stats["size"], n)
        for i in range(n):
            rows.append(
                {
                    "monster": f"{tribe[:3]}-{idx + i + 1}",
                    "speed": float(np.clip(speed[i], 5, 100)),
                    "strength": float(np.clip(strength[i], 5, 100)),
                    "size": float(np.clip(size[i], 5, 100)),
                    "tribe": tribe,
                }
            )
        idx += n
    return pd.DataFrame(rows)
def render() -> None:
    level_header(
        3,
        "Monsters flood the arena with different speed, strength, and size. "
        "Use K-Means to group similar creatures. Correct tribes unlock the gate.",
    )
    lesson(
        "K-Means clustering partitions points into k groups by nearest centroid. "
        "Choosing k well matters: too few merges tribes, too many splits a single tribe into fragments."
    )
    df = _monsters()
    visible = df.drop(columns=["tribe"])
    st.subheader("Arena scouting report")
    st.dataframe(visible.head(15), use_container_width=True, hide_index=True)
    st.caption("Tribe labels are hidden from you — that is the puzzle.")
    c1, c2, c3 = st.columns(3)
    with c1:
        k = st.slider("Number of tribes (k)", 2, 8, 4)
    with c2:
        x_feat = st.selectbox("X axis", FEATURES, index=0)
    with c3:
        y_feat = st.selectbox("Y axis", FEATURES, index=1)
    use_feats = st.multiselect("Cluster using features", FEATURES, default=FEATURES)
    if st.button("Run K-Means grouping", type="primary"):
        if len(use_feats) < 2:
            st.session_state.level_3_result = (
                False,
                "Need at least two features so the tribes can separate in space.",
                None,
            )
        elif x_feat == y_feat:
            st.session_state.level_3_result = (
                False,
                "Pick two different axes to see the grouping.",
                None,
            )
        else:
            scaler = StandardScaler()
            x = scaler.fit_transform(df[use_feats])
            model = KMeans(n_clusters=k, n_init=10, random_state=0)
            labels = model.fit_predict(x)
            ari = float(adjusted_rand_score(df["tribe"], labels))
            plot_df = df.copy()
            plot_df["cluster"] = labels.astype(str)
            if k == 3 and ari >= ARI_WIN:
                msg = (
                    f"k=3 recovered the Swiftling, Ironhide, and Mystic tribes (ARI {ari:.2f}). The gate opens."
                )
                ok = True
            elif k < 3:
                msg = (
                    f"k={k} glues different tribes together (ARI {ari:.2f}). The arena has more than {k} kinds of monster."
                )
                ok = False
            elif k > 3:
                msg = (
                    f"k={k} over-splits the tribes (ARI {ari:.2f}). Extra clusters fracture creatures that belong together."
                )
                ok = False
            else:
                msg = (
                    f"k is right but the feature mix is weak (ARI {ari:.2f}). Include speed, strength, and size so the three blobs separate."
                )
                ok = False
            st.session_state.level_3_result = (ok, msg, (plot_df, x_feat, y_feat, ari))
    if "level_3_result" in st.session_state:
        ok, msg, payload = st.session_state.level_3_result
        if payload:
            plot_df, px_feat, py_feat, ari = payload
            fig = px.scatter(
                plot_df,
                x=px_feat,
                y=py_feat,
                color="cluster",
                hover_data=["monster", "speed", "strength", "size"],
                title="Monster clusters",
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#e8f0ea",
            )
            st.plotly_chart(fig, use_container_width=True)
            st.metric("Agreement with hidden tribes (Adjusted Rand Index)", f"{ari:.2f}")
        if ok:
            win_banner(3, msg)
        else:
            fail_banner(msg)