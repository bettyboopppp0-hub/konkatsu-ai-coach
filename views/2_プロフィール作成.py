import streamlit as st

from core import TONES, ask_json, copyable, settings_block, settings_bar

st.title("プロフィール作成")
st.caption("文章を書く必要はありません。選ぶだけでAIがゼロから作ります。")

s = settings_bar()

HOBBIES = [
    "映画・ドラマ", "カフェ巡り", "旅行", "料理", "食べ歩き", "音楽・ライブ",
    "読書", "アニメ・漫画", "ゲーム", "筋トレ・ジム", "ランニング", "登山・キャンプ",
    "サウナ", "写真", "ドライブ", "スポーツ観戦", "美術館・展示", "ペット", "推し活",
]
PERSONALITY = [
    "おだやか", "明るい", "聞き上手", "マイペース", "面倒見がいい", "素直",
    "好奇心旺盛", "こつこつ努力型", "笑いのツボが浅い", "インドア寄り", "アウトドア寄り",
]
DATE_IDEAS = ["カフェでまったり", "ごはん・飲み", "映画", "水族館・動物園", "ドライブ", "散歩・公園", "スポーツ観戦", "旅行"]

col1, col2 = st.columns(2)
with col1:
    job = st.text_input("お仕事", placeholder="例: IT系の営業、看護師、電気工事士")
    area = st.text_input("住んでいるエリア", placeholder="例: 福岡市内、東京23区")
with col2:
    holiday = st.selectbox("休日", ["土日", "平日休み", "シフト制", "不定休"])
    style = st.selectbox("文章のトーン", TONES)

hobbies = st.multiselect("趣味・好きなこと(3〜5個)", HOBBIES)
personality = st.multiselect("性格(2〜4個)", PERSONALITY)
dates = st.multiselect("一緒にしたいこと", DATE_IDEAS)
free = st.text_area(
    "自由に伝えたいこと(任意)",
    height=80,
    placeholder="例: 最近サウナにハマっている、実家で猫を飼っている、来年までに結婚したい",
)

PROMPT = """次の情報をもとに、マッチングアプリのプロフィール文をゼロから作成してください。

{settings}

【本人の情報】
- 仕事: {job}
- エリア: {area}
- 休日: {holiday}
- 趣味: {hobbies}
- 性格: {personality}
- 一緒にしたいこと: {dates}
- 自由記述: {free}
- 希望トーン: {style}

以下のJSON形式で出力してください。すべて日本語。

{{
  "versions": [
    {{"label": "本命案", "text": "プロフィール全文", "score": 想定スコア(整数), "point": "この案の狙いを一言"}},
    {{"label": "別案", "text": "プロフィール全文", "score": 想定スコア(整数), "point": "この案の狙いを一言"}}
  ],
  "hooks": ["相手が食いつきやすい「ツッコミどころ」として仕込んだ要素", "..."],
  "advice": "この人がこのアプリで気をつけるべきことを2文"
}}

条件:
- {app}の文化・文字数感に合わせる
- 「誠実です」「普通です」のような中身のない表現は使わない
- 伏せ字(◯◯)や空欄は使わず、与えられた情報の範囲で自然に書ききる
- 情報が足りない部分は無理に創作せず、書かずに済ませる
"""

if st.button("プロフィールを作成する", type="primary", disabled=not (job and hobbies)):
    with st.spinner("AIが作成しています..."):
        st.session_state["made"] = ask_json(
            PROMPT.format(
                settings=settings_block(s),
                job=job,
                area=area or "未記入",
                holiday=holiday,
                hobbies="、".join(hobbies) or "未記入",
                personality="、".join(personality) or "未記入",
                dates="、".join(dates) or "未記入",
                free=free or "なし",
                style=style,
                app=s["app"],
            )
        )

result = st.session_state.get("made")

if result:
    st.divider()
    versions = result.get("versions", [])
    if versions:
        tabs = st.tabs([f"{v.get('label','案')} {v.get('score','')}点" for v in versions])
        for tab, v in zip(tabs, versions):
            with tab:
                st.caption(f"🎯 {v.get('point','')}")
                copyable(v.get("text", ""))

    hooks = result.get("hooks", [])
    if hooks:
        st.markdown("#### 🪝 仕込んだ会話のきっかけ")
        for h in hooks:
            st.markdown(f"- {h}")

    advice = result.get("advice")
    if advice:
        st.success(advice)
