import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&display=swap');

:root {
  --pink: #ff5c8a;
  --violet: #6c5ce7;
  --sky: #3ec6ff;
  --mint: #0fc9a0;
  --text: #1b1f2a;
  --muted: #7b8494;
  --line: rgba(27,31,42,0.08);
  --card: rgba(255,255,255,0.78);
  --shadow: 0 6px 28px -10px rgba(80,60,180,0.20);
  --shadow-lg: 0 14px 46px -16px rgba(80,60,180,0.30);
}

.stApp {
  background:
    radial-gradient(1000px 520px at 8% -12%, rgba(255,92,138,0.13), transparent 58%),
    radial-gradient(880px 480px at 94% 2%, rgba(108,92,231,0.13), transparent 60%),
    radial-gradient(760px 620px at 50% 108%, rgba(62,198,255,0.11), transparent 62%),
    #fdfcff;
}

.stMainBlockContainer { position: relative; z-index: 1; padding-top: 2.2rem; }

html, body, .stApp, p, div, span, label, li, button {
  font-family: 'Outfit', -apple-system, 'Hiragino Sans', 'Yu Gothic UI', 'Meiryo', sans-serif;
  color: var(--text);
}

h1 {
  font-weight: 800 !important;
  letter-spacing: -0.025em;
  background: linear-gradient(100deg, var(--pink) 0%, var(--violet) 58%, var(--sky) 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

h2, h3 { color: var(--text) !important; letter-spacing: -0.015em; font-weight: 700 !important; }

h4 {
  font-size: 0.95rem !important;
  font-weight: 700 !important;
  color: var(--text) !important;
  padding-left: 11px !important;
  margin-top: 1.7rem !important;
  border-left: 3px solid transparent;
  border-image: linear-gradient(180deg, var(--pink), var(--violet)) 1;
}

[data-testid="stCaptionContainer"], .stCaption, [data-testid="stCaptionContainer"] p {
  color: var(--muted) !important;
}

[data-testid="stSidebar"] {
  background: rgba(255,255,255,0.82);
  border-right: 1px solid var(--line);
  backdrop-filter: blur(20px);
}
[data-testid="stSidebarNav"] a { border-radius: 10px !important; transition: all 0.16s ease; }
[data-testid="stSidebarNav"] a:hover { background: rgba(108,92,231,0.08) !important; }
[data-testid="stSidebarNav"] a[aria-current="page"] {
  background: linear-gradient(90deg, rgba(255,92,138,0.14), rgba(108,92,231,0.10)) !important;
  box-shadow: inset 2px 0 0 var(--violet);
}

.stButton > button, .stFormSubmitButton > button {
  border-radius: 14px;
  border: 1px solid var(--line);
  background: rgba(255,255,255,0.9);
  color: var(--text);
  font-weight: 600;
  box-shadow: var(--shadow);
  transition: all 0.18s cubic-bezier(0.2,0.8,0.2,1);
}
.stButton > button:hover {
  border-color: rgba(108,92,231,0.35);
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
  color: var(--violet);
}
.stButton > button[kind="primary"] {
  background: linear-gradient(100deg, var(--pink) 0%, var(--violet) 100%);
  border: none;
  color: #fff !important;
  font-weight: 700;
  box-shadow: 0 10px 30px -10px rgba(255,92,138,0.75);
}
.stButton > button[kind="primary"]:hover {
  filter: brightness(1.05);
  color: #fff !important;
  box-shadow: 0 16px 40px -12px rgba(108,92,231,0.8);
}
.stButton > button[kind="primary"] p { color: #fff !important; }
.stButton > button:disabled { opacity: 0.4; box-shadow: none; transform: none; }

textarea, input, [data-baseweb="select"] > div, [data-baseweb="input"] {
  background: rgba(255,255,255,0.92) !important;
  border: 1px solid var(--line) !important;
  border-radius: 14px !important;
  color: var(--text) !important;
}
textarea:focus, input:focus {
  border-color: rgba(108,92,231,0.5) !important;
  box-shadow: 0 0 0 4px rgba(108,92,231,0.10) !important;
}

[data-testid="stExpander"] {
  border: 1px solid var(--line) !important;
  border-radius: 16px !important;
  background: var(--card);
  backdrop-filter: blur(14px);
  box-shadow: var(--shadow);
  overflow: hidden;
}
[data-testid="stExpander"] summary:hover { color: var(--violet); }

.stTabs [data-baseweb="tab-list"] { gap: 6px; border-bottom: 1px solid var(--line); }
.stTabs [data-baseweb="tab"] {
  border-radius: 12px 12px 0 0;
  color: var(--muted);
  font-weight: 600;
  padding: 9px 14px;
}
.stTabs [aria-selected="true"] {
  color: var(--violet) !important;
  background: linear-gradient(180deg, rgba(108,92,231,0.10), transparent);
}
.stTabs [data-baseweb="tab-highlight"] {
  background: linear-gradient(90deg, var(--pink), var(--violet));
}

[data-testid="stAlertContainer"] {
  border-radius: 15px;
  border: 1px solid var(--line);
  box-shadow: var(--shadow);
  backdrop-filter: blur(10px);
}

.stCode, pre {
  background: rgba(108,92,231,0.05) !important;
  border: 1px solid rgba(108,92,231,0.16) !important;
  border-radius: 14px !important;
}
.stCode code {
  color: var(--text) !important;
  font-family: 'Outfit', 'Hiragino Sans', sans-serif !important;
  line-height: 1.85 !important;
}

hr { border-color: var(--line) !important; }

[data-testid="stChatMessage"] {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 16px;
  box-shadow: var(--shadow);
  backdrop-filter: blur(8px);
}

[data-testid="stMetricValue"] {
  font-weight: 800;
  background: linear-gradient(100deg, var(--pink), var(--violet));
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

[data-testid="stFileUploaderDropzone"] {
  background: rgba(255,255,255,0.85) !important;
  border: 1.5px dashed rgba(108,92,231,0.32) !important;
  border-radius: 16px !important;
}

[data-testid="stHeader"] { background: transparent; }

@keyframes hud-in { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: none; } }
.hud-panel {
  animation: hud-in 0.42s cubic-bezier(0.2,0.8,0.2,1) both;
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 20px;
  box-shadow: var(--shadow);
  backdrop-filter: blur(14px);
}

.worry-grid ~ [data-testid="stElementContainer"] .stButton > button {
  padding: 16px 18px;
  border-radius: 18px;
  background: rgba(255,255,255,0.85);
  line-height: 1.6;
  animation: hud-in 0.4s ease both;
}
.worry-grid ~ [data-testid="stElementContainer"] .stButton > button p {
  font-size: 0.98rem;
  color: var(--text);
}
.worry-grid ~ [data-testid="stElementContainer"] .stButton > button:hover p { color: var(--violet); }

@media (max-width: 640px) {
  .stMainBlockContainer {
    padding-top: 1.1rem !important;
    padding-left: 0.9rem !important;
    padding-right: 0.9rem !important;
  }
  h1 { font-size: 1.65rem !important; line-height: 1.3 !important; }
  h2 { font-size: 1.25rem !important; }
  h3 { font-size: 1.08rem !important; }
  h4 { font-size: 0.92rem !important; margin-top: 1.3rem !important; }

  .stButton > button, .stFormSubmitButton > button { min-height: 48px; font-size: 0.95rem; }
  .stButton > button[kind="primary"] { min-height: 54px; font-size: 1rem; }

  textarea, input { font-size: 16px !important; }

  .stTabs [data-baseweb="tab-list"] { overflow-x: auto; flex-wrap: nowrap; }
  .stTabs [data-baseweb="tab"] { font-size: 0.82rem; padding: 8px 11px; white-space: nowrap; }

  .stCode code { font-size: 0.86rem !important; }
}
</style>
"""


def inject():
    st.markdown(CSS, unsafe_allow_html=True)
