import streamlit as st

from core import ask_json, copyable, settings_block, settings_bar

st.title("デートプラン")
st.caption("エリアと予算から、初回デートのプランと誘い方をまとめて作ります。")

s = settings_bar()

col1, col2 = st.columns(2)
with col1:
    area = st.text_input("エリア", placeholder="例: 福岡市天神、東京・渋谷")
    budget = st.select_slider("1人あたりの予算", ["〜2,000円", "〜3,000円", "〜5,000円", "〜8,000円", "〜12,000円"], value="〜5,000円")
with col2:
    timing = st.selectbox("時間帯", ["昼(ランチ・カフェ)", "夕方(お茶〜軽く食事)", "夜(ディナー)"])
    duration = st.selectbox("想定の長さ", ["1〜2時間(初回向け)", "2〜3時間", "半日"])

their_interests = st.text_input("相手の趣味・好きなもの", placeholder="例: カフェ巡り、映画、猫が好き")

PROMPT = """初回デートのプランを提案してください。

{settings}

【条件】
- エリア: {area}
- 予算: {budget}(1人あたり)
- 時間帯: {timing}
- 想定の長さ: {duration}
- 相手の趣味: {interests}

以下のJSON形式で出力してください。すべて日本語。

{{
  "plans": [
    {{
      "title": "プラン名",
      "flow": ["時間の流れを3〜4ステップで", "..."],
      "cost": "想定費用",
      "why": "この相手に合う理由を一言",
      "risk": "気をつける点を一言"
    }}
  ],
  "invite_messages": [
    {{"label": "自然に誘う型", "text": "そのまま送れる誘い文句"}},
    {{"label": "日程を決めきる型", "text": "そのまま送れる誘い文句"}}
  ],
  "manners": ["初回デートで印象を落とさないための注意点", "..."]
}}

条件:
- plansは3つ
- 実在しそうにない店名を断定で書かない。「〇〇系のカフェ」のようにジャンルで示すか、そのエリアで一般的に知られた場所の種類で表現する
- 初回は長すぎず、解散しやすい構成にする
- 誘い文句は重すぎず、断りやすさを残した言い方にする
"""

if st.button("プランを作る", type="primary", disabled=not area.strip()):
    with st.spinner("AIが考えています..."):
        st.session_state["plan"] = ask_json(
            PROMPT.format(
                settings=settings_block(s),
                area=area,
                budget=budget,
                timing=timing,
                duration=duration,
                interests=their_interests or "(未入力)",
            )
        )

result = st.session_state.get("plan")

if result:
    st.divider()
    plans = result.get("plans", [])
    if plans:
        st.markdown("#### 🗺 デートプラン")
        tabs = st.tabs([p.get("title", "プラン") for p in plans])
        for tab, p in zip(tabs, plans):
            with tab:
                for i, step in enumerate(p.get("flow", []), 1):
                    st.markdown(f"**{i}.** {step}")
                st.caption(f"💰 {p.get('cost','')}")
                st.caption(f"👍 {p.get('why','')}")
                st.caption(f"⚠️ {p.get('risk','')}")

    invites = result.get("invite_messages", [])
    if invites:
        st.markdown("#### ✉️ 誘い方")
        for inv in invites:
            st.markdown(f"**{inv.get('label','')}**")
            copyable(inv.get("text", ""))

    manners = result.get("manners", [])
    if manners:
        st.markdown("#### 🎯 初回デートの注意点")
        for m in manners:
            st.markdown(f"- {m}")
