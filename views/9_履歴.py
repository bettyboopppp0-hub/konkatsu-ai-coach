import json
import os

import streamlit as st

from core import HISTORY_FILE, load_history, score_color, settings_bar

st.title("診断履歴")
st.caption("これまでの診断結果です。このPC内にだけ保存されています。")

settings_bar()

history = load_history()

if not history:
    st.info("まだ診断履歴がありません。")
    st.stop()

scored = [h for h in history if h.get("score") is not None]
if len(scored) >= 2:
    latest = scored[0]["score"]
    oldest = scored[-1]["score"]
    col1, col2, col3 = st.columns(3)
    col1.metric("最新スコア", f"{latest}点")
    col2.metric("初回スコア", f"{oldest}点")
    col3.metric("変化", f"{latest - oldest:+d}点")
    st.line_chart(
        {"スコア": [h["score"] for h in reversed(scored)]},
        height=180,
    )
    st.divider()

for item in history:
    score = item.get("score")
    badge = (
        f"<span style='color:{score_color(score)};font-weight:700;'>{score}点</span>"
        if score is not None
        else ""
    )
    detail = f" / {item['detail']}" if item.get("detail") else ""
    st.markdown(
        f"<div class='hud-panel' style='padding:11px 15px;margin-bottom:9px;'>"
        f"<div style='font-size:0.74rem;color:#a4abb8;letter-spacing:0.05em;'>{item['at']} · {item['kind']}{detail}</div>"
        f"<div style='font-size:0.88rem;color:#4a5263;margin-top:5px;line-height:1.55;'>{item['summary']} {badge}</div></div>",
        unsafe_allow_html=True,
    )

st.divider()
if st.button("履歴をすべて削除", type="secondary"):
    try:
        os.remove(HISTORY_FILE)
    except OSError:
        pass
    st.rerun()
