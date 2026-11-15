import streamlit as st
from game.state import complete_level, get_level, go_ending, go_map, is_completed
def win_banner(level_id: int, extra: str = "") -> None:
    level = get_level(level_id)
    already = is_completed(level_id)
    complete_level(level_id)
    xp_note = "" if already else f" You gained {level['xp']} XP."
    st.markdown(
        f"<div class='dq-win'><b>World restored:</b> {level['name']}.{xp_note} {extra}</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div class='dq-lesson'><b>{level['concept']}</b> — {level['mission']}.</div>",
        unsafe_allow_html=True,
    )
    cols = st.columns(2)
    with cols[0]:
        if st.button("Continue to map", key=f"win_map_{level_id}", use_container_width=True):
            go_map()
            st.rerun()
    if level_id == 6:
        with cols[1]:
            if st.button("Face the restored kingdom", key="win_ending", use_container_width=True):
                go_ending()
                st.rerun()
def fail_banner(message: str) -> None:
    st.markdown(f"<div class='dq-fail'><b>The corruption holds.</b> {message}</div>", unsafe_allow_html=True)
def lesson(text: str) -> None:
    st.markdown(f"<div class='dq-lesson'>{text}</div>", unsafe_allow_html=True)
def level_header(level_id: int, blurb: str) -> None:
    level = get_level(level_id)
    st.markdown(f"## {level['emoji']} {level['name']}")
    st.caption(f"Mission: {level['mission']}  ·  Concept: {level['concept']}")
    st.write(blurb)
    if st.button("← Back to map", key=f"back_{level_id}"):
        go_map()
        st.rerun()