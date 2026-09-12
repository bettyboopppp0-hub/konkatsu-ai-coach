import streamlit as st

from core import (
    ask_json_with_image,
    before_after,
    score_bars,
    settings_block,
    settings_bar,
)

st.title("写真・スクショ診断")
st.caption("プロフィール写真やアプリのスクショをアップするだけ。第一印象を数値で診断します。")

s = settings_bar()

uploaded = st.file_uploader(
    "写真またはプロフィールのスクリーンショット",
    type=["png", "jpg", "jpeg", "webp"],
    help="顔がはっきり写っている必要はありません。雰囲気・構図・清潔感を診断します。",
)

if uploaded:
    st.image(uploaded, width=280)

PROMPT = """アップロードされたマッチングアプリ用の写真(またはプロフィールのスクリーンショット)を診断してください。

{settings}

以下のJSON形式で出力してください。すべて日本語。

{{
  "type": "この画像が「プロフィール写真」か「アプリのスクリーンショット」か",
  "score": 第一印象の総合スコア(0-100の整数。厳しめ),
  "potential": 改善した場合に到達できるスコア(整数),
  "score_breakdown": {{
    "清潔感": 0-100,
    "表情・雰囲気": 0-100,
    "構図・画質": 0-100,
    "背景・場所": 0-100,
    "人柄の伝わりやすさ": 0-100
  }},
  "first_impression": "相手({target})がこの写真を見た瞬間の本音を、その人になりきって一人称で3文。忖度なし",
  "good_points": ["この写真の良いところ", "..."],
  "issues": [
    {{"problem": "マイナスになっている点", "fix": "どう直すか具体的に"}}
  ],
  "next_shot": "次に撮るべき写真の具体的な指示を、撮影場所・服装・構図・時間帯まで含めて3文",
  "photo_set": ["1枚目に置くべき写真", "2枚目に置くべき写真", "3枚目に置くべき写真"]
}}

条件:
- 容姿そのものの良し悪しは評価しない。撮り方・見せ方の改善に集中する
- 人物が特定できる情報(実名など)には触れない
- 実行可能な指示にする。「プロに撮ってもらう」で終わらせない
"""

if st.button("写真を診断する", type="primary", disabled=uploaded is None):
    with st.spinner("AIが診断しています..."):
        st.session_state["photo"] = ask_json_with_image(
            PROMPT.format(settings=settings_block(s), target=s["target"]),
            uploaded.getvalue(),
            uploaded.type,
        )

result = st.session_state.get("photo")

if result:
    st.divider()
    st.caption(f"判定: {result.get('type','')}")
    before_after(int(result.get("score", 0)), int(result.get("potential", 0)))

    st.markdown("#### 項目別スコア")
    score_bars(result.get("score_breakdown", {}))

    st.markdown(f"#### 🗣 {s['target']}から見た本音")
    st.info(result.get("first_impression", ""))

    good = result.get("good_points", [])
    if good:
        st.markdown("#### ✅ 良い点")
        for g in good:
            st.markdown(f"- {g}")

    issues = result.get("issues", [])
    if issues:
        st.markdown("#### ⚠️ 改善点")
        for item in issues:
            st.warning(f"**{item.get('problem','')}**\n\n➡️ {item.get('fix','')}")

    nxt = result.get("next_shot")
    if nxt:
        st.markdown("#### 📸 次に撮るべき写真")
        st.success(nxt)

    photo_set = result.get("photo_set", [])
    if photo_set:
        st.markdown("#### 🖼 写真の並べ方(おすすめ)")
        for i, p in enumerate(photo_set, 1):
            st.markdown(f"**{i}枚目** — {p}")
