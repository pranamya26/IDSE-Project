import streamlit as st
LEVELS = [
    {
        "id": 1,
        "key": "missing_village",
        "name": "Missing Village",
        "mission": "Find and repair missing data",
        "concept": "Data cleaning",
        "xp": 100,
        "emoji": "🏘️",
    },
    {
        "id": 2,
        "key": "forest",
        "name": "Forest of Patterns",
        "mission": "Discover hidden relationships",
        "concept": "Correlation",
        "xp": 100,
        "emoji": "🌲",
    },
    {
        "id": 3,
        "key": "monster_arena",
        "name": "Monster Arena",
        "mission": "Group similar monsters",
        "concept": "Clustering",
        "xp": 120,
        "emoji": "👾",
    },
    {
        "id": 4,
        "key": "prediction_bridge",
        "name": "Prediction Bridge",
        "mission": "Predict which bridge is safe",
        "concept": "Classification",
        "xp": 120,
        "emoji": "🌉",
    },
    {
        "id": 5,
        "key": "overfitting_castle",
        "name": "Overfitting Castle",
        "mission": "Train a model that works on new situations",
        "concept": "Overfitting",
        "xp": 150,
        "emoji": "🏰",
    },
    {
        "id": 6,
        "key": "final_boss",
        "name": "Final Boss",
        "mission": "Build the best predictive model",
        "concept": "Model evaluation",
        "xp": 200,
        "emoji": "👑",
    },
]
def init_state() -> None:
    defaults = {
        "initialized": True,
        "page": "home",
        "player_name": "Wanderer",
        "xp": 0,
        "unlocked": [1],
        "completed": [],
        "current_level": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
def reset_run() -> None:
    st.session_state.page = "home"
    st.session_state.xp = 0
    st.session_state.unlocked = [1]
    st.session_state.completed = []
    st.session_state.current_level = None
    for key in list(st.session_state.keys()):
        if key.startswith("data_") or key.startswith("level_"):
            del st.session_state[key]
def get_level(level_id: int) -> dict:
    return next(level for level in LEVELS if level["id"] == level_id)
def is_unlocked(level_id: int) -> bool:
    return level_id in st.session_state.unlocked
def is_completed(level_id: int) -> bool:
    return level_id in st.session_state.completed
def complete_level(level_id: int) -> None:
    level = get_level(level_id)
    if level_id not in st.session_state.completed:
        st.session_state.completed = st.session_state.completed + [level_id]
        st.session_state.xp += level["xp"]
    nxt = level_id + 1
    if nxt <= 6 and nxt not in st.session_state.unlocked:
        st.session_state.unlocked = st.session_state.unlocked + [nxt]
def go_home() -> None:
    st.session_state.page = "home"
def go_map() -> None:
    st.session_state.page = "map"
    st.session_state.current_level = None
def go_level(level_id: int) -> None:
    if is_unlocked(level_id):
        st.session_state.page = f"level_{level_id}"
        st.session_state.current_level = level_id
def go_ending() -> None:
    st.session_state.page = "ending"