import streamlit as st

from core import (
    ask_json_with_image,
    before_after,
    copyable,
    save_history,
    score_bars,
    settings_block,
    settings_bar,
)

st.title("スクショ診断")
st.caption("プロフィール画面をスクショして貼るだけ。相手が実際に見ている1画面を、そのまま採点します。")

s = settings_bar()

mode = st.radio(
    "何を見てもらいますか",
    ["プロフィール画面まるごと(写真＋文章)", "写真だけ"],
    horizontal=False,
)

uploaded = st.file_uploader(
    "スクリーンショット",
    type=["png", "jpg", "jpeg", "webp"],
    help="スマホでプロフィールを開いて、そのままスクショしたものを貼ってください。",
)

if uploaded:
    st.image(uploaded, width=260)

WHOLE_PROMPT = """アップロードされたマッチングアプリのプロフィール画面(スクリーンショット)を診断してください。
相手が実際にスワイプ中に見ている1画面として、写真と文章を「セット」で評価します。

{settings}

以下のJSON形式で出力してください。すべて日本語。

{{
  "score": この1画面の総合スコア(0-100の整数。厳しめ),
  "potential": 改善後に到達できるスコア(整数),
  "swipe_verdict": "「いいねする」「保留」「スルー」のいずれか1つ",
  "score_breakdown": {{
    "写真の印象": 0-100,
    "文章の中身": 0-100,
    "情報量": 0-100,
    "写真と文章の一貫性": 0-100,
    "会話のフック": 0-100
  }},
  "first_impression": "相手({target})がこの画面を3秒見たときに頭に浮かぶ本音を、その人になりきって一人称で3文。忖度なし",
  "mismatch": "写真と文章がちぐはぐになっている点。ズレがなければ「ズレはありません」とだけ書く",
  "photo_issues": [{{"problem": "写真側のマイナス点", "fix": "どう直すか具体的に"}}],
  "text_issues": [{{"problem": "文章側のマイナス点", "fix": "どう直すか具体的に"}}],
  "revised_text": "スクショから読み取れた文章をもとに書き直した、改善後のプロフィール全文",
  "biggest_win": "今いちばん先に直すべき1つと、それで何点上がるかを1文で"
}}

条件:
- 画面から文字が読み取れる場合は、その文章を実際に引用して指摘する
- 容姿そのものの良し悪しは評価しない。撮り方・見せ方・文章との組み合わせに集中する
- 実名など人物が特定できる情報には触れない
- 文章が読み取れない場合、text_issuesとrevised_textは「文章が読み取れませんでした」とだけ書く
"""

PHOTO_PROMPT = """アップロードされたマッチングアプリ用の写真を診断してください。

{settings}

以下のJSON形式で出力してください。すべて日本語。

{{
  "score": 第一印象の総合スコア(0-100の整数。厳しめ),
  "potential": 改善後に到達できるスコア(整数),
  "swipe_verdict": "「いいねする」「保留」「スルー」のいずれか1つ",
  "score_breakdown": {{
    "清潔感": 0-100, "表情・雰囲気": 0-100, "構図・画質": 0-100,
    "背景・場所": 0-100, "人柄の伝わりやすさ": 0-100
  }},
  "first_impression": "相手({target})がこの写真を見た瞬間の本音を、その人になりきって一人称で3文。忖度なし",
  "photo_issues": [{{"problem": "マイナスになっている点", "fix": "どう直すか具体的に"}}],
  "next_shot": "次に撮るべき写真の指示を、場所・服装・構図・時間帯まで含めて3文",
  "photo_set": ["1枚目に置くべき写真", "2枚目に置くべき写真", "3枚目に置くべき写真"],
  "biggest_win": "今いちばん先に直すべき1つと、それで何点上がるかを1文で"
}}

条件:
- 容姿そのものの良し悪しは評価しない。撮り方・見せ方の改善に集中する
- 人物が特定できる情報には触れない
- 「プロに撮ってもらう」で終わらせず、自分で実行できる指示にする
"""

is_whole = mode.startswith("プロフィール画面")

if st.button("診断する", type="primary", disabled=uploaded is None):
    with st.spinner("AIが診断しています..."):
        prompt = (WHOLE_PROMPT if is_whole else PHOTO_PROMPT).format(
            settings=settings_block(s), target=s["target"]
        )
        result = ask_json_with_image(prompt, uploaded.getvalue(), uploaded.type)
        st.session_state["shot"] = result
        st.session_state["shot_mode"] = mode
        save_history("スクショ診断" if is_whole else "写真診断", mode, result.get("score"))

result = st.session_state.get("shot")

if result and st.session_state.get("shot_mode") == mode:
    st.divider()
    before_after(int(result.get("score", 0)), int(result.get("potential", 0)))

    verdict = result.get("swipe_verdict", "")
    verdict_color = {"いいねする": "#0fc9a0", "保留": "#f59f00", "スルー": "#ff5c8a"}.get(verdict, "#7b8494")
    st.markdown(
        f"<div style='text-align:center;margin:2px 0 22px;'>"
        f"<div style='font-size:0.76rem;color:#7b8494;letter-spacing:0.1em;'>この画面を見た相手は</div>"
        f"<div style='display:inline-block;margin-top:7px;padding:5px 20px;border-radius:99px;"
        f"font-size:1.1rem;font-weight:800;color:#fff;background:{verdict_color};"
        f"box-shadow:0 8px 22px -8px {verdict_color};'>{verdict}</div></div>",
        unsafe_allow_html=True,
    )

    win = result.get("biggest_win")
    if win:
        st.success(f"🎯 まずここを直す — {win}")

    st.markdown("#### 項目別スコア")
    score_bars(result.get("score_breakdown", {}))

    st.markdown(f"#### 🗣 {s['target']}から見た本音")
    st.info(result.get("first_impression", ""))

    mismatch = result.get("mismatch")
    if mismatch and "ズレはありません" not in mismatch:
        st.markdown("#### ⚡ 写真と文章のちぐはぐ")
        st.warning(mismatch)

    photo_issues = result.get("photo_issues", [])
    if photo_issues:
        st.markdown("#### 📷 写真の改善点")
        for item in photo_issues:
            st.warning(f"**{item.get('problem','')}**\n\n➡️ {item.get('fix','')}")

    text_issues = result.get("text_issues", [])
    if text_issues:
        st.markdown("#### ✍️ 文章の改善点")
        for item in text_issues:
            st.warning(f"**{item.get('problem','')}**\n\n➡️ {item.get('fix','')}")

    revised = result.get("revised_text")
    if revised and "読み取れません" not in revised:
        st.markdown("#### 📝 書き直した文章")
        copyable(revised)

    nxt = result.get("next_shot")
    if nxt:
        st.markdown("#### 📸 次に撮るべき写真")
        st.success(nxt)

    photo_set = result.get("photo_set", [])
    if photo_set:
        st.markdown("#### 🖼 写真の並べ方")
        for i, p in enumerate(photo_set, 1):
            st.markdown(f"**{i}枚目** — {p}")
