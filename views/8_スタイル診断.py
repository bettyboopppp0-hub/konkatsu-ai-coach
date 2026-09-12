import streamlit as st

from core import (
    ask_json,
    ask_json_with_image,
    before_after,
    save_history,
    score_bars,
    settings_block,
    settings_bar,
)

st.title("スタイル診断")
st.caption("初デートの服装、写真に写る服。清潔感が伝わるコーデをAIが具体的に指定します。")

s = settings_bar()

mode = st.radio("診断のしかた", ["服装の写真を見てもらう", "条件からコーデを提案してもらう"], horizontal=False)

SCENES = {
    "プロフィール写真用": "1枚目のメイン写真で着る服。清潔感と親しみやすさの両立が最優先",
    "初デート(カフェ・ランチ)": "昼間の短時間。気合いを入れすぎない、こなれた印象",
    "初デート(ディナー)": "夜の食事。少しきちんと感を出しつつ、堅すぎない",
    "2回目以降のデート": "少し素を出す。相手との距離が縮まる自然さ",
    "結婚相談所のお見合い": "第一印象が全て。清潔感・誠実さ・信頼感を最優先",
}

BUDGETS = ["〜5,000円", "〜10,000円", "〜20,000円", "〜40,000円", "こだわらない"]

COMMON = """
条件:
- 「清潔感を出しましょう」のような抽象論で終わらせない。アイテム・色・シルエット・素材まで具体的に指定する
- ユニクロ・GU・無印良品・ZARAなど、実際に買える価格帯の店で揃う前提で提案する
- 特定のブランドの実在しない商品名を断定で書かない。アイテムの種類と色・形で示す
- 体型や容姿そのものを否定しない。見せ方の工夫に集中する
"""

if mode == "服装の写真を見てもらう":
    uploaded = st.file_uploader("服装が写っている写真", type=["png", "jpg", "jpeg", "webp"])
    scene = st.selectbox("どの場面で着る服か", list(SCENES))
    if uploaded:
        st.image(uploaded, width=260)

    PROMPT = """アップロードされた服装の写真を、マッチングアプリ・婚活の観点から診断してください。

{settings}

【想定シーン】{scene} — {scene_note}

以下のJSON形式で出力してください。すべて日本語。

{{
  "score": 現状の総合スコア(0-100の整数。厳しめ),
  "potential": 改善後に到達できるスコア(整数),
  "score_breakdown": {{
    "清潔感": 0-100, "サイズ感": 0-100, "色の組み立て": 0-100,
    "TPO適合": 0-100, "親しみやすさ": 0-100
  }},
  "first_impression": "相手({target})がこの服装の人と会った瞬間の本音を、その人になりきって一人称で3文。忖度なし",
  "good_points": ["この服装の良いところ", "..."],
  "issues": [{{"problem": "マイナスになっている点", "fix": "どう直すか具体的に"}}],
  "shopping_list": [{{"item": "買い足すべきアイテム", "detail": "色・形・素材・選び方の基準", "budget": "価格の目安"}}],
  "summary": "この人が守るべき服装のルールを2文で"
}}
""" + COMMON

    if st.button("服装を診断する", type="primary", disabled=uploaded is None):
        with st.spinner("AIが診断しています..."):
            result = ask_json_with_image(
                PROMPT.format(settings=settings_block(s), scene=scene, scene_note=SCENES[scene], target=s["target"]),
                uploaded.getvalue(),
                uploaded.type,
            )
            st.session_state["style"] = result
            save_history("スタイル診断", f"{scene}の服装", result.get("score"))

else:
    col1, col2 = st.columns(2)
    with col1:
        scene = st.selectbox("場面", list(SCENES))
        season = st.selectbox("季節", ["春", "夏", "秋", "冬"])
    with col2:
        budget = st.select_slider("予算", BUDGETS, value="〜10,000円")
        body = st.selectbox("体型", ["細身", "標準", "がっちり", "ぽっちゃり", "気にしていない"])
    worry = st.text_input("服装の悩み(任意)", placeholder="例: 何を着ても地味になる、サイズ感が分からない")

    PROMPT = """次の条件に合うコーディネートを提案してください。

{settings}

【条件】
- 場面: {scene} — {scene_note}
- 季節: {season}
- 予算: {budget}
- 体型: {body}
- 悩み: {worry}

以下のJSON形式で出力してください。すべて日本語。

{{
  "outfits": [
    {{
      "title": "コーデ名",
      "items": [{{"part": "トップス/ボトムス/靴/小物など", "detail": "色・形・素材まで具体的に"}}],
      "why": "この場面でこの相手に効く理由を一言",
      "budget": "合計の目安金額",
      "ng": "このコーデでやってはいけないこと一言"
    }}
  ],
  "rules": ["この人が服選びで守るべきルール", "..."],
  "avoid": ["婚活の場で避けるべき服装", "..."]
}}

outfitsは3つ。
""" + COMMON

    if st.button("コーデを提案してもらう", type="primary"):
        with st.spinner("AIが考えています..."):
            result = ask_json(
                PROMPT.format(
                    settings=settings_block(s),
                    scene=scene,
                    scene_note=SCENES[scene],
                    season=season,
                    budget=budget,
                    body=body,
                    worry=worry or "特になし",
                )
            )
            st.session_state["style_outfit"] = result
            save_history("コーデ提案", f"{season}・{scene}")

result = st.session_state.get("style")
if mode == "服装の写真を見てもらう" and result:
    st.divider()
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

    shopping = result.get("shopping_list", [])
    if shopping:
        st.markdown("#### 🛍 買い足しリスト")
        for item in shopping:
            st.markdown(f"**{item.get('item','')}** — {item.get('detail','')}  \n<small>目安: {item.get('budget','')}</small>", unsafe_allow_html=True)

    if result.get("summary"):
        st.success(result["summary"])

outfit = st.session_state.get("style_outfit")
if mode != "服装の写真を見てもらう" and outfit:
    st.divider()
    outfits = outfit.get("outfits", [])
    if outfits:
        tabs = st.tabs([o.get("title", "コーデ") for o in outfits])
        for tab, o in zip(tabs, outfits):
            with tab:
                for item in o.get("items", []):
                    st.markdown(f"**{item.get('part','')}** — {item.get('detail','')}")
                st.caption(f"💰 {o.get('budget','')}")
                st.caption(f"👍 {o.get('why','')}")
                st.caption(f"⚠️ {o.get('ng','')}")

    rules = outfit.get("rules", [])
    if rules:
        st.markdown("#### 📏 あなたが守るべきルール")
        for r in rules:
            st.markdown(f"- {r}")

    avoid = outfit.get("avoid", [])
    if avoid:
        st.markdown("#### ❌ 婚活で避けるべき服装")
        for a in avoid:
            st.markdown(f"- {a}")
