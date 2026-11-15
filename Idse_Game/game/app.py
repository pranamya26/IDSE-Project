import streamlit as st
from game.state import (
    LEVELS,
    go_home,
    go_level,
    go_map,
    init_state,
    is_completed,
    is_unlocked,
    reset_run,
)
from game.styles import inject
from game.levels import (
    final_boss,
    forest,
    missing_village,
    monster_arena,
    overfitting_castle,
    prediction_bridge,
)
st.set_page_config(
    page_title="Data Quest: The Lost World",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)
init_state()
inject()
RENDERERS = {
    1: missing_village.render,
    2: forest.render,
    3: monster_arena.render,
    4: prediction_bridge.render,
    5: overfitting_castle.render,
    6: final_boss.render,
}
def sidebar() -> None:
    st.sidebar.markdown("### 🗺️ Data Quest")
    st.sidebar.caption("The Lost World")
    name = st.sidebar.text_input("Player name", value=st.session_state.player_name)
    st.session_state.player_name = name or "Wanderer"
    st.sidebar.metric("XP", st.session_state.xp)
    st.sidebar.metric("Worlds restored", f"{len(st.session_state.completed)} / 6")
    current = st.session_state.current_level
    if current:
        level = next(lv for lv in LEVELS if lv["id"] == current)
        st.sidebar.write(f"Now exploring: **{level['name']}**")
    st.sidebar.divider()
    if st.sidebar.button("Home", use_container_width=True):
        go_home()
        st.rerun()
    if st.sidebar.button("World map", use_container_width=True):
        go_map()
        st.rerun()
    if st.sidebar.button("Reset run", use_container_width=True):
        reset_run()
        st.rerun()
def render_home() -> None:
    st.markdown("<h1 class='dq-title'>Data Quest — The Lost World</h1>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="dq-hero">
          <div class="dq-banner left">
            <div class="art">🌸🌿🧚‍♀️</div>
            <div class="caption">The Data Kingdom, before the fall</div>
          </div>
          <div class="dq-banner right">
            <div class="art">🏯🌙🤖</div>
            <div class="caption">An evil AI corrupts every world</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="dq-story">
          <b>Story:</b> An evil AI has corrupted the Data Kingdom.
          The player must travel through different worlds to restore the kingdom.<br/><br/>
          Each world represents a Data Science concept.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
    c1, c2, _ = st.columns([1, 1, 2])
    started = bool(st.session_state.completed)
    with c1:
        label = "Continue" if started else "Begin the quest"
        if st.button(label, type="primary", use_container_width=True):
            go_map()
            st.rerun()
    with c2:
        if started and st.button("New run", use_container_width=True):
            reset_run()
            st.rerun()
def render_map() -> None:
    st.markdown("<h1 class='dq-title'>World Map</h1>", unsafe_allow_html=True)
    st.write("Restore each world in order. Locked lands stay sealed until the previous concept is mastered.")
    rows = [LEVELS[:3], LEVELS[3:]]
    for row in rows:
        cols = st.columns(3)
        for col, level in zip(cols, row):
            unlocked = is_unlocked(level["id"])
            done = is_completed(level["id"])
            status = "Restored" if done else ("Open" if unlocked else "Locked")
            locked_class = "" if unlocked else " locked"
            with col:
                st.markdown(
                    f"""
                    <div class="dq-card{locked_class}">
                      <span class="dq-pill">{status}</span>
                      <h3>{level["emoji"]} {level["id"]}. {level["name"]}</h3>
                      <p class="meta"><b>Game mission:</b> {level["mission"]}</p>
                      <p class="meta"><b>Data Science concept:</b> {level["concept"]}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if unlocked:
                    if st.button(
                        "Enter" if not done else "Revisit",
                        key=f"enter_{level['id']}",
                        use_container_width=True,
                    ):
                        go_level(level["id"])
                        st.rerun()
                else:
                    st.button("Sealed", key=f"lock_{level['id']}", disabled=True, use_container_width=True)
def render_ending() -> None:
    st.markdown("<h1 class='dq-title'>The Data Kingdom Restored</h1>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="dq-story">
          {st.session_state.player_name}, the six worlds stand clear of the AI's fog.
          Villages keep honest records, forests reveal true bonds, tribes stand grouped,
          bridges hold, models generalize, and evaluation — not vanity — decides the throne.
          You finish with <b>{st.session_state.xp} XP</b>.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.balloons()
    if st.button("Return to map"):
        go_map()
        st.rerun()
sidebar()
page = st.session_state.page
if page == "home":
    render_home()
elif page == "map":
    render_map()
elif page == "ending":
    render_ending()
elif page.startswith("level_"):
    level_id = int(page.split("_")[1])
    if not is_unlocked(level_id):
        st.warning("That world is still sealed.")
        render_map()
    else:
        RENDERERS[level_id]()
else:
    render_home()