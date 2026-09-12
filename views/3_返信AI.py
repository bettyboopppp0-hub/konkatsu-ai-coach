import streamlit as st

from core import ask_json, copyable, settings_block, settings_bar

st.title("返信AI")
st.caption("相手のメッセージを貼るだけ。会話が続く返信を3パターン作ります。")

s = settings_bar()

history = st.text_area(
    "これまでのやり取り(任意)",
    height=110,
    placeholder="相手: はじめまして！\n自分: はじめまして、メッセージありがとうございます！",
)
last = st.text_area(
    "相手からの最新メッセージ",
    height=110,
    placeholder="例: 映画好きなんですね！最近何か観ましたか？",
)
goal = st.radio(
    "この返信のゴール",
    ["会話を広げたい", "距離を縮めたい", "デートに誘いたい", "返事が途絶えた相手を戻したい"],
    horizontal=False,
)

PROMPT = """マッチングアプリのメッセージに対する返信を作ってください。

{settings}

【これまでのやり取り】
{history}

【相手からの最新メッセージ】
{last}

【この返信で達成したいこと】
{goal}

以下のJSON形式で出力してください。すべて日本語。

{{
  "read": "この最新メッセージから読み取れる相手の温度感・意図を2文で。脈ありかどうかも率直に",
  "replies": [
    {{"label": "無難・安全型", "text": "返信文", "why": "この返信が効く理由を一言", "risk": "気をつける点を一言"}},
    {{"label": "距離を縮める型", "text": "返信文", "why": "...", "risk": "..."}},
    {{"label": "一歩踏み込む型", "text": "返信文", "why": "...", "risk": "..."}}
  ],
  "ng": ["この場面でやりがちなNG返信", "..."],
  "timing": "返信するべきタイミングの目安を一言"
}}

条件:
- 返信文はそのままコピーして送れる完成形にする。伏せ字(◯◯)は使わない
- 長すぎない。相手のメッセージと同じか少し長いくらいの分量に合わせる
- 質問攻めにしない。自分の話と相手への質問のバランスを取る
"""

if st.button("返信を作る", type="primary", disabled=not last.strip()):
    with st.spinner("AIが考えています..."):
        st.session_state["reply"] = ask_json(
            PROMPT.format(
                settings=settings_block(s),
                history=history or "(やり取りの履歴なし。最初のメッセージへの返信)",
                last=last,
                goal=goal,
            )
        )

result = st.session_state.get("reply")

if result:
    st.divider()
    st.markdown("#### 🔍 相手の温度感")
    st.info(result.get("read", ""))

    replies = result.get("replies", [])
    if replies:
        st.markdown("#### ✉️ 返信案")
        tabs = st.tabs([r.get("label", "案") for r in replies])
        for tab, r in zip(tabs, replies):
            with tab:
                copyable(r.get("text", ""))
                st.caption(f"👍 {r.get('why','')}")
                st.caption(f"⚠️ {r.get('risk','')}")

    ng = result.get("ng", [])
    if ng:
        st.markdown("#### ❌ この場面でのNG返信")
        for item in ng:
            st.markdown(f"- {item}")

    timing = result.get("timing")
    if timing:
        st.success(f"⏰ {timing}")
