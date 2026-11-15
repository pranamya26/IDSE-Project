import numpy as np
import pandas as pd
import streamlit as st
from game.ui import fail_banner, lesson, level_header, win_banner
MIN_VILLAGERS = 30
NAMES = [
    "Asha", "Bram", "Cira", "Dalen", "Elowen", "Fen", "Grita", "Halsi",
    "Ivo", "Jora", "Kell", "Lumi", "Mira", "Nox", "Orin", "Pia",
    "Quill", "Ryn", "Sable", "Tovin", "Uma", "Vex", "Wren", "Xan",
    "Yara", "Zed", "Nori", "Pell", "Rook", "Sage", "Tess", "Ulric",
    "Vale", "Wisp", "Yor", "Zinn", "Oats", "Kira", "Lark", "Moss",
]
def _raw_village() -> pd.DataFrame:
    rng = np.random.default_rng(7)
    n = 40
    age = rng.integers(12, 72, size=n).astype(float)
    gold = rng.integers(4, 90, size=n).astype(float)
    health = rng.integers(40, 100, size=n).astype(float)
    miss_age = rng.choice(n, 8, replace=False)
    miss_gold = rng.choice(n, 7, replace=False)
    miss_health = rng.choice(n, 6, replace=False)
    age[miss_age] = np.nan
    gold[miss_gold] = np.nan
    health[miss_health] = np.nan
    age[2] = -8
    age[11] = 240
    gold[5] = -30
    df = pd.DataFrame(
        {
            "name": NAMES[:n],
            "age": age,
            "gold": gold,
            "health": health,
        }
    )
    df.loc[19, "gold"] = np.nan
    return df
def _cleaned(raw: pd.DataFrame, age_fill: str, gold_fill: str, health_fill: str, fix_invalid: bool) -> pd.DataFrame:
    df = raw.copy()
    if fix_invalid:
        invalid_age = (df["age"] < 0) | (df["age"] > 100)
        df.loc[invalid_age, "age"] = np.nan
        df.loc[df["gold"] < 0, "gold"] = np.nan
    def fill_numeric(series: pd.Series, method: str) -> pd.Series:
        if method == "Mean":
            return series.fillna(series.mean())
        if method == "Median":
            return series.fillna(series.median())
        if method == "Drop rows with missing values":
            return series
        return series
    if age_fill != "Drop rows with missing values":
        df["age"] = fill_numeric(df["age"], age_fill)
    if gold_fill != "Drop rows with missing values":
        df["gold"] = fill_numeric(df["gold"], gold_fill)
    if health_fill != "Drop rows with missing values":
        df["health"] = fill_numeric(df["health"], health_fill)
    if (
        age_fill == "Drop rows with missing values"
        or gold_fill == "Drop rows with missing values"
        or health_fill == "Drop rows with missing values"
    ):
        df = df.dropna(subset=["age", "gold", "health"])
    df["age"] = df["age"].round(1)
    df["gold"] = df["gold"].round(1)
    df["health"] = df["health"].round(1)
    return df.reset_index(drop=True)
def _evaluate(cleaned: pd.DataFrame) -> tuple[bool, str]:
    missing = int(cleaned[["age", "gold", "health"]].isna().sum().sum())
    invalid_age = int(((cleaned["age"] < 0) | (cleaned["age"] > 100)).sum()) if len(cleaned) else 0
    invalid_gold = int((cleaned["gold"] < 0).sum()) if len(cleaned) else 0
    n = len(cleaned)
    if missing:
        return False, f"{missing} missing values remain. Impute or carefully drop them — empty cells still hide villagers."
    if invalid_age or invalid_gold:
        return False, "Impossible ages or negative gold remain. Turn on 'Repair cursed values' so outliers become missing, then impute."
    if n < MIN_VILLAGERS:
        return False, f"Only {n} villagers survived the repair. Dropping every incomplete row starves the village — impute instead of deleting everyone."
    return True, f"All {n} remaining records are complete and valid. The village remembers its people."
def render() -> None:
    level_header(
        1,
        "The census scrolls are torn. Ages vanish, gold turns to dust, and a few numbers are cursed. "
        "Restore the village register without erasing too many lives.",
    )
    lesson(
        "Missing data is common. Dropping every incomplete row can throw away signal. "
        "Imputation (mean/median) keeps the census usable when values are missing at random."
    )
    raw = _raw_village()
    st.subheader("Torn census")
    st.dataframe(raw, use_container_width=True, hide_index=True)
    miss = raw[["age", "gold", "health"]].isna().sum()
    st.caption(
        f"Missing — age: {int(miss['age'])}, gold: {int(miss['gold'])}, health: {int(miss['health'])}. "
        "Watch for cursed ages (-8, 240) and negative gold."
    )
    options = ["Mean", "Median", "Drop rows with missing values"]
    c1, c2, c3 = st.columns(3)
    with c1:
        age_fill = st.selectbox("Repair age with", options, index=1)
    with c2:
        gold_fill = st.selectbox("Repair gold with", options, index=1)
    with c3:
        health_fill = st.selectbox("Repair health with", options, index=0)
    fix_invalid = st.checkbox("Repair cursed values (invalid age / negative gold)", value=True)
    if st.button("Cast repair spell", type="primary"):
        cleaned = _cleaned(raw, age_fill, gold_fill, health_fill, fix_invalid)
        st.session_state.level_1_cleaned = cleaned
        ok, msg = _evaluate(cleaned)
        st.session_state.level_1_result = (ok, msg)
    if "level_1_cleaned" in st.session_state:
        st.subheader("Restored census")
        st.dataframe(st.session_state.level_1_cleaned, use_container_width=True, hide_index=True)
        ok, msg = st.session_state.level_1_result
        if ok:
            win_banner(1, msg)
        else:
            fail_banner(msg)