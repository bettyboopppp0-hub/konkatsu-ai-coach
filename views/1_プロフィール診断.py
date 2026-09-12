import streamlit as st

from core import (
    TONES,
    app_preview,
    ask_json,
    before_after,
    copyable,
    save_history,
    score_bars,
    settings_block,
    settings_bar,
)

st.title("プロフィール診断")
st.caption("今のプロフィールを貼るだけ。スコア・NG表現・相手目線の本音まで、30秒で丸わかり。")

s = settings_bar()

EXAMPLE = "はじめまして！都内で営業の仕事をしています。趣味は映画鑑賞とカフェ巡りです。休日はだいたい家でゴロゴロしてます。気軽にいいねしてください！よろしくお願いします。"

if st.button("例文を入れて試す", type="secondary"):
    st.session_state["profile_text"] = EXAMPLE

text = st.text_area(
    "今のプロフィール文を貼り付けてください",
    height=200,
    key="profile_text",
    placeholder="例: 30代前半、都内でIT系の仕事をしています。休日は登山やカフェ巡りが好きです。",
)

st.caption(f"{len(text)} 文字")

PROMPT = """次のマッチングアプリのプロフィール文を診断し、改善案を作ってください。

{settings}

【診断対象のプロフィール文】
{text}

以下のJSON形式で出力してください。すべて日本語。

{{
  "score": 現状の総合スコア(0-100の整数。厳しめに採点する),
  "score_breakdown": {{
    "具体性": 0-100,
    "親しみやすさ": 0-100,
    "誠実さ": 0-100,
    "会話誘導力": 0-100,
    "ユニーク度": 0-100
  }},
  "first_impression": "相手({target})がこのプロフを見た瞬間に頭に浮かぶ本音を、その人になりきって一人称で3文。忖度なし。良いところも悪いところも正直に",
  "swipe_verdict": "「いいねする」「保留」「スルー」のいずれか1つ",
  "ng_phrases": [
    {{"phrase": "本文から抜き出したNG表現", "reason": "なぜマイナスか", "better": "こう書き換える"}}
  ],
  "good_points": ["今のままでも効いている点", "..."],
  "improvement_points": [
    {{"before": "元の表現", "after": "改善後の表現", "gain": 加点の目安(整数), "reason": "なぜ上がるか"}}
  ],
  "revised_versions": [
    {{"label": "{tone0}", "text": "改善後の全文", "score": 改善後の想定スコア(整数), "target": "どんな相手に刺さるか一言"}},
    {{"label": "{tone1}", "text": "改善後の全文", "score": 改善後の想定スコア(整数), "target": "どんな相手に刺さるか一言"}},
    {{"label": "{tone2}", "text": "改善後の全文", "score": 改善後の想定スコア(整数), "target": "どんな相手に刺さるか一言"}}
  ],
  "app_tip": "{app}というアプリ特有の、このプロフに対する具体的なアドバイスを2文"
}}

改善後の全文は{app}の文化・文字数感に合わせること。空欄や伏せ字(◯◯)は使わず、書ける範囲で自然な具体例を入れること。
ng_phrasesは該当がなければ空配列。improvement_pointsは2〜4個。
"""

if st.button("プロフィールを診断する", type="primary", disabled=not text.strip()):
    with st.spinner("AIが診断しています..."):
        diag = ask_json(
            PROMPT.format(
                settings=settings_block(s),
                text=text,
                target=s["target"],
                app=s["app"],
                tone0=TONES[0],
                tone1=TONES[1],
                tone2=TONES[2],
            )
        )
        st.session_state["diag"] = diag
        save_history("プロフィール診断", text, diag.get("score"), detail=s["app"])

result = st.session_state.get("diag")

if result:
    st.divider()

    versions = result.get("revised_versions", [])
    best = max((v.get("score", 0) for v in versions), default=result.get("score", 0))
    before_after(int(result.get("score", 0)), int(best))

    verdict = result.get("swipe_verdict", "")
    verdict_color = {"いいねする": "#0fc9a0", "保留": "#f59f00", "スルー": "#ff5c8a"}.get(verdict, "#7b8494")
    st.markdown(
        f"<div style='text-align:center;margin:2px 0 22px;'>"
        f"<div style='font-size:0.76rem;color:#7b8494;letter-spacing:0.1em;'>今のままだと相手は</div>"
        f"<div style='display:inline-block;margin-top:7px;padding:5px 20px;border-radius:99px;"
        f"font-size:1.1rem;font-weight:800;color:#fff;background:{verdict_color};"
        f"box-shadow:0 8px 22px -8px {verdict_color};'>{verdict}</div></div>",
        unsafe_allow_html=True,
    )

    st.markdown("#### 項目別スコア")
    score_bars(result.get("score_breakdown", {}))

    st.markdown(f"#### 🗣 {s['target']}から見た本音")
    st.info(result.get("first_impression", ""))

    ng = result.get("ng_phrases", [])
    if ng:
        st.markdown(f"#### ⚠️ NG表現 {len(ng)}件")
        for item in ng:
            st.warning(f"**「{item.get('phrase','')}」**\n\n{item.get('reason','')}\n\n➡️ {item.get('better','')}")

    good = result.get("good_points", [])
    if good:
        st.markdown("#### ✅ 良い点")
        for p in good:
            st.markdown(f"- {p}")

    improvements = result.get("improvement_points", [])
    if improvements:
        st.markdown("#### 💡 改善ポイント")
        for item in improvements:
            st.markdown(
                f"""
                <div class="hud-panel" style="padding:13px 16px;margin-bottom:11px;">
                  <div style="color:#a4abb8;text-decoration:line-through;font-size:0.85rem;">{item.get('before','')}</div>
                  <div style="margin:7px 0;font-size:0.94rem;line-height:1.65;">
                    {item.get('after','')}
                    <span style="font-size:0.76rem;font-weight:800;color:#fff;background:#0fc9a0;
                                 border-radius:99px;padding:2px 9px;margin-left:5px;
                                 white-space:nowrap;">+{item.get('gain',0)}</span>
                  </div>
                  <div style="font-size:0.8rem;color:#7b8494;">{item.get('reason','')}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    if versions:
        st.markdown("#### ✏️ 改善後プロフィール(3パターン)")
        tabs = st.tabs([f"{v.get('label','案')} {v.get('score','')}点" for v in versions])
        for tab, v in zip(tabs, versions):
            with tab:
                st.caption(f"🎯 {v.get('target','')}")
                copyable(v.get("text", ""))
                with st.expander(f"📱 {s['app']} の画面でどう見えるか"):
                    app_preview(s["app"], v.get("text", ""), s["age"])

    tip = result.get("app_tip")
    if tip:
        st.markdown(f"#### 📱 {s['app']} 向けアドバイス")
        st.success(tip)

    st.divider()
    if st.button("🎮 このプロフで会話の練習をする", use_container_width=True):
        st.switch_page("views/6_会話シミュレーション.py")
