CSS = """
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700&family=Source+Sans+3:wght@400;600;700&display=swap');
html, body, [data-testid="stAppViewContainer"] {
  background: radial-gradient(1200px 600px at 10% -10%, #1b3d2f 0%, transparent 50%),
              radial-gradient(900px 500px at 110% 10%, #3a2a12 0%, transparent 45%),
              linear-gradient(180deg, #07110d 0%, #0d1c16 45%, #08140f 100%);
  color: #e8f0ea;
  font-family: "Source Sans 3", sans-serif;
}
[data-testid="stHeader"] {
  background: transparent;
}
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0a1611 0%, #12241b 100%);
  border-right: 1px solid #2d5a45;
}
h1, h2, h3, .dq-title {
  font-family: "Cinzel", serif !important;
  letter-spacing: 0.04em;
  color: #f4e2b0 !important;
}
.dq-hero {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin: 8px 0 22px 0;
}
.dq-banner {
  border-radius: 18px;
  min-height: 210px;
  padding: 22px;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  border: 1px solid rgba(244, 226, 176, 0.25);
  box-shadow: 0 18px 40px rgba(0, 0, 0, 0.35);
}
.dq-banner.left {
  background:
    linear-gradient(180deg, rgba(8,20,15,0.15) 0%, rgba(8,20,15,0.72) 70%),
    radial-gradient(circle at 30% 30%, #7ad39a 0%, transparent 42%),
    linear-gradient(135deg, #245c3d 0%, #6b3a1a 55%, #1a3a4a 100%);
}
.dq-banner.right {
  background:
    linear-gradient(180deg, rgba(8,20,15,0.1) 0%, rgba(8,20,15,0.75) 75%),
    radial-gradient(circle at 70% 20%, #f4d27a 0%, transparent 40%),
    linear-gradient(135deg, #16324a 0%, #2e5e3f 50%, #5a2a6b 100%);
}
.dq-banner .art {
  font-size: 42px;
  line-height: 1.2;
}
.dq-banner .caption {
  color: #f4e2b0;
  font-family: "Cinzel", serif;
  font-size: 18px;
  margin-top: 8px;
}
.dq-story {
  background: rgba(12, 28, 22, 0.72);
  border: 1px solid #3d6b52;
  border-radius: 16px;
  padding: 18px 20px;
  color: #d7e8dc;
  font-size: 1.05rem;
  line-height: 1.55;
}
.dq-card {
  background: linear-gradient(180deg, rgba(18, 40, 30, 0.92), rgba(10, 22, 17, 0.92));
  border: 1px solid #3a6b51;
  border-radius: 16px;
  padding: 16px;
  min-height: 180px;
  box-shadow: inset 0 1px 0 rgba(244, 226, 176, 0.08);
}
.dq-card.locked {
  opacity: 0.45;
  filter: grayscale(0.4);
}
.dq-card .meta {
  color: #9fc9b2;
  font-size: 0.92rem;
}
.dq-pill {
  display: inline-block;
  background: #1e4634;
  color: #f4e2b0;
  border: 1px solid #c9a24a;
  border-radius: 999px;
  padding: 2px 10px;
  font-size: 0.78rem;
  font-family: "Cinzel", serif;
}
.dq-win {
  background: linear-gradient(90deg, #1d4d32, #245c3d);
  border: 1px solid #f4e2b0;
  color: #f8f3e3;
  padding: 14px 16px;
  border-radius: 12px;
  margin: 10px 0 16px 0;
}
.dq-fail {
  background: linear-gradient(90deg, #4a1f1f, #5a2a22);
  border: 1px solid #e0a090;
  color: #fde8e2;
  padding: 14px 16px;
  border-radius: 12px;
  margin: 10px 0 16px 0;
}
.dq-lesson {
  background: rgba(30, 50, 70, 0.55);
  border-left: 4px solid #c9a24a;
  padding: 12px 14px;
  border-radius: 0 10px 10px 0;
  color: #e6eef5;
}
.stButton > button {
  background: linear-gradient(180deg, #c9a24a, #8a6a24);
  color: #14110a;
  border: 0;
  font-weight: 700;
  border-radius: 10px;
}
.stButton > button:hover {
  filter: brightness(1.08);
  border: 0;
  color: #14110a;
}
[data-testid="stMetricValue"] {
  color: #f4e2b0;
}
"""
def inject() -> None:
    import streamlit as st
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)