import streamlit as st

from core import ask_json, copyable, settings_block, settings_bar

st.title("初回メッセージ")
st.caption("相手のプロフィールを貼るだけ。返信が来る最初の一通を作ります。")

s = settings_bar()

their_profile = st.text_area(
    "相手のプロフィール文",
    height=180,
    placeholder="相手のプロフィール文をそのまま貼り付けてください",
)
my_profile = st.text_area(
    "自分のプロフィール(任意)",
    height=90,
    placeholder="自分の情報があると、共通点を踏まえた文面になります",
)

PROMPT = """マッチング後に送る「最初の一通」を作ってください。

{settings}

【相手のプロフィール】
{their}

【自分のプロフィール】
{mine}

以下のJSON形式で出力してください。すべて日本語。

{{
  "reading": "相手のプロフから読み取れる人物像・地雷になりそうな点を3文",
  "hooks": ["相手のプロフの中で触れるべきポイント(具体的に引用)", "..."],
  "messages": [
    {{"label": "王道・安心型", "text": "初回メッセージ全文", "why": "狙いを一言"}},
    {{"label": "共通点フック型", "text": "初回メッセージ全文", "why": "狙いを一言"}},
    {{"label": "軽さ・ユーモア型", "text": "初回メッセージ全文", "why": "狙いを一言"}}
  ],
  "ng": ["この相手に送ってはいけない内容", "..."],
  "reply_rate": "返信率を上げるために特に効く一手を1文"
}}

条件:
- 「はじめまして！よろしくお願いします」だけの中身のない文にしない
- 相手のプロフィールの具体的な部分に必ず触れる
- 長すぎない(3〜5文程度)。重いと引かれる
- 容姿への言及は避ける。地雷になりやすい
- 伏せ字(◯◯)は使わず、そのまま送れる完成形にする
"""

if st.button("初回メッセージを作る", type="primary", disabled=not their_profile.strip()):
    with st.spinner("AIが考えています..."):
        st.session_state["first"] = ask_json(
            PROMPT.format(
                settings=settings_block(s),
                their=their_profile,
                mine=my_profile or "(未入力)",
            )
        )

result = st.session_state.get("first")

if result:
    st.divider()
    st.markdown("#### 🔍 相手の読み解き")
    st.info(result.get("reading", ""))

    hooks = result.get("hooks", [])
    if hooks:
        st.markdown("#### 🪝 触れるべきポイント")
        for h in hooks:
            st.markdown(f"- {h}")

    messages = result.get("messages", [])
    if messages:
        st.markdown("#### ✉️ 初回メッセージ案")
        tabs = st.tabs([m.get("label", "案") for m in messages])
        for tab, m in zip(tabs, messages):
            with tab:
                copyable(m.get("text", ""))
                st.caption(f"👍 {m.get('why','')}")

    ng = result.get("ng", [])
    if ng:
        st.markdown("#### ❌ この相手へのNG")
        for item in ng:
            st.markdown(f"- {item}")

    tip = result.get("reply_rate")
    if tip:
        st.success(f"📈 {tip}")
