import streamlit as st

from core import ask_json, score_color, settings_block, settings_bar

st.title("会話シミュレーション")
st.caption("AIが相手役になります。本番前に、好感度の上がり下がりを見ながら会話を練習できます。")

s = settings_bar()

TYPES = {
    "慎重・警戒気味": "初対面には壁がある。信頼できると感じるまで短文で返す。軽いノリは苦手",
    "明るい・ノリがいい": "テンポよく返す。楽しい空気を求める。重い話や長文は苦手",
    "受け身・聞き役": "自分から話題を振るのが苦手。質問されると答えるが、広げるのは相手任せ",
    "真剣・婚活モード": "条件や価値観をシビアに見ている。遊び目的を警戒。将来の話を重視",
}

if "sim_started" not in st.session_state:
    st.session_state["sim_started"] = False

if not st.session_state["sim_started"]:
    st.markdown("#### 相手の設定")
    col1, col2 = st.columns(2)
    with col1:
        their_age = st.slider("相手の年齢", 18, 60, 30, key="sim_age")
    with col2:
        their_type = st.selectbox("相手のタイプ", list(TYPES), key="sim_type")
    st.caption(TYPES[their_type])
    scene = st.selectbox(
        "シチュエーション",
        ["マッチング直後(最初の一通から)", "何往復かした後", "そろそろデートに誘いたい場面"],
        key="sim_scene",
    )

    if st.button("シミュレーションを始める", type="primary"):
        st.session_state["sim_started"] = True
        st.session_state["sim_messages"] = []
        st.session_state["sim_affinity"] = 50
        st.session_state["sim_config"] = {
            "age": their_age,
            "type": their_type,
            "type_note": TYPES[their_type],
            "scene": scene,
        }
        st.rerun()
    st.stop()

cfg = st.session_state["sim_config"]
affinity = st.session_state["sim_affinity"]

st.markdown(
    f"""
    <div style="margin-bottom:6px;">
      <div style="display:flex;justify-content:space-between;font-size:0.85rem;">
        <span>相手の好感度</span>
        <span style="color:{score_color(affinity)};font-weight:700;">{affinity}</span>
      </div>
      <div style="background:#eee;border-radius:99px;height:9px;overflow:hidden;">
        <div style="width:{affinity}%;height:100%;background:{score_color(affinity)};"></div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.caption(f"相手: {cfg['age']}歳 / {cfg['type']} — {cfg['scene']}")

for msg in st.session_state["sim_messages"]:
    with st.chat_message("user" if msg["role"] == "me" else "assistant"):
        st.write(msg["text"])
        if msg.get("coach"):
            delta = msg["coach"].get("delta", 0)
            sign = f"+{delta}" if delta >= 0 else str(delta)
            color = "green" if delta >= 0 else "red"
            st.caption(f"🎯 好感度 :{color}[**{sign}**] — {msg['coach'].get('comment','')}")

PROMPT = """マッチングアプリの会話シミュレーションを進行してください。あなたは2つの役割を同時に担います。

役割1: 相手役({target}、{age}歳、タイプ: {type_note})として、自然に返信する
役割2: コーチとして、利用者が今送ったメッセージを採点する

{settings}

【シチュエーション】{scene}

【これまでの会話】
{history}

【利用者が今送ったメッセージ】
{message}

【現在の好感度】{affinity} / 100

以下のJSON形式で出力してください。すべて日本語。

{{
  "reply": "相手役としての返信。キャラクターを崩さず、その人が実際に返しそうな長さ・テンションで",
  "delta": 今のメッセージによる好感度の増減(-15〜+15の整数。忖度せず厳しく判定),
  "comment": "コーチとして、今のメッセージの良し悪しを1文で。悪い場合ははっきり指摘する",
  "hint": "次にどう返すと良いかのヒントを1文"
}}

条件:
- 好感度が下がる内容(自分語り、質問攻め、いきなり距離を詰める、タメ口、容姿への言及など)は容赦なく減点する
- 相手役の返信は、好感度が低いときは短く冷たく、高いときは自分から話題を広げる
- 相手役は絵文字を使いすぎない。自然な日本語で
"""

if user_input := st.chat_input("メッセージを入力"):
    history = "\n".join(
        f"{'利用者' if m['role'] == 'me' else '相手'}: {m['text']}" for m in st.session_state["sim_messages"]
    )
    st.session_state["sim_messages"].append({"role": "me", "text": user_input})

    with st.spinner("相手が入力中..."):
        result = ask_json(
            PROMPT.format(
                settings=settings_block(s),
                target=s["target"],
                age=cfg["age"],
                type_note=cfg["type_note"],
                scene=cfg["scene"],
                history=history or "(まだ会話なし)",
                message=user_input,
                affinity=affinity,
            )
        )

    delta = int(result.get("delta", 0))
    st.session_state["sim_affinity"] = max(0, min(100, affinity + delta))
    st.session_state["sim_messages"][-1]["coach"] = {
        "delta": delta,
        "comment": result.get("comment", ""),
    }
    st.session_state["sim_messages"].append({"role": "them", "text": result.get("reply", "")})
    st.session_state["sim_hint"] = result.get("hint", "")
    st.rerun()

hint = st.session_state.get("sim_hint")
if hint:
    st.info(f"💡 次の一手: {hint}")

col1, col2 = st.columns(2)
with col1:
    if st.button("最初からやり直す"):
        st.session_state["sim_started"] = False
        st.session_state.pop("sim_hint", None)
        st.rerun()
with col2:
    if st.button("総評を見る", type="primary", disabled=len(st.session_state["sim_messages"]) < 2):
        history = "\n".join(
            f"{'利用者' if m['role'] == 'me' else '相手'}: {m['text']}" for m in st.session_state["sim_messages"]
        )
        with st.spinner("総評を作成中..."):
            review = ask_json(
                f"""次の会話シミュレーションの結果を総評してください。

{settings_block(s)}

【会話全文】
{history}

【最終好感度】{st.session_state['sim_affinity']} / 100

以下のJSON形式で出力してください。すべて日本語。

{{
  "verdict": "この会話の到達点(「デートに誘える」「もう少し必要」「立て直しが必要」のいずれか)",
  "good": ["良かった点", "..."],
  "bad": ["直すべき癖", "..."],
  "next_action": "次に実際のやり取りで意識すべきことを2文"
}}"""
            )
        st.session_state["sim_review"] = review

review = st.session_state.get("sim_review")
if review:
    st.divider()
    st.markdown(f"### 📋 総評: {review.get('verdict','')}")
    good = review.get("good", [])
    if good:
        st.markdown("**✅ 良かった点**")
        for g in good:
            st.markdown(f"- {g}")
    bad = review.get("bad", [])
    if bad:
        st.markdown("**⚠️ 直すべき癖**")
        for b in bad:
            st.markdown(f"- {b}")
    st.success(review.get("next_action", ""))
