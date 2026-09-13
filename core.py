import inspect
import json
import os
import time

import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import errors, types
from streamlit.errors import StreamlitAPIException

import theme

MODELS = ["gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.5-flash"]

APPS = {
    "Pairs": "真面目な恋活〜婚活層が中心。誠実さ・安心感・丁寧な文章量(300〜500字)が好まれる",
    "タップル": "20代中心でカジュアル。趣味でつながる文化。趣味の具体性と軽いノリが重要。長文は重い",
    "with": "心理テスト・価値観重視。内面や性格の言語化、価値観の共通点提示が刺さる",
    "Tinder": "短文・カジュアル。長文は読まれない。1〜3行でユーモアと勢いを出す",
    "Bumble": "女性から先にメッセージを送る文化。女性が話しかけやすいフック(質問・ツッコミどころ)が必須",
    "Omiai": "婚活寄り。結婚観・将来像・経済的な安定感が見られる",
    "マリッシュ": "再婚・シンママ/シンパパ歓迎層が多い。包容力と現実的な生活感が響く",
    "東カレデート": "審査制のハイスペ層。洗練された簡潔さ、背伸びしない品の良さ",
    "ブライダルネット": (
        "IBJ運営の婚活特化サービス。恋活ではなく結婚が前提で、会員は全員有料のため真剣度が高い。"
        "結婚希望時期・子どもの希望・家事分担・親との同居など条件項目が細かく、そこと自己紹介文の整合性が見られる。"
        "日記機能があり、日記の積み重ねで人柄を判断されるのが最大の特徴。"
        "軽いノリやその場のテンションより、生活感・誠実さ・将来像の具体性が響く"
    ),
}

PURPOSES = {
    "婚活(結婚前提)": "1〜2年以内の結婚を見据えている。誠実さ・将来像・生活感の一致が最重要",
    "恋活(まず恋人)": "まず恋人が欲しい。楽しさ・相性・一緒にいる時間の想像しやすさが重要",
    "再婚活": "離婚歴あり。包容力・現実的な生活観・子どもへの理解が重要",
    "まず友達から": "気軽な出会い重視。ハードルの低さと共通の趣味が重要",
}

TONES = ["誠実・王道", "カジュアル・親しみ", "ユーモア・個性"]

BASE_PERSONA = """あなたは婚活・恋活マッチングアプリの専門コーチです。
机上の一般論ではなく、実際に何年も婚活を続けて数百人とやり取りしてきた当事者の肌感覚で答えてください。

守ること:
- 「誠実です」「真面目です」のような、誰でも書ける中身のない言葉は評価しない
- 固有名詞・数字・具体的なエピソードが入っているかを重視する
- 相手が返信しやすい「ツッコミどころ」があるかを重視する
- 建前のきれいごとではなく、実際にスワイプされる/されない基準で判断する
- 相手を傷つけないが、忖度もしない。改善すべき点ははっきり伝える
- 「◯◯」のような伏せ字や穴埋めは絶対に使わない。相手の名前が不明なときは名前を使わずに書く
"""


@st.cache_resource
def get_client():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        try:
            api_key = st.secrets["GEMINI_API_KEY"]
        except (KeyError, FileNotFoundError, StreamlitAPIException):
            return None
    return genai.Client(api_key=api_key)


def require_client():
    client = get_client()
    if client is None:
        st.error("GEMINI_API_KEY が設定されていません。プロジェクトフォルダの .env ファイルを確認してください。")
        st.stop()
    return client


FREE_DAILY_LIMIT = 3
GLOBAL_DAILY_CAP = 300

PLANS = [
    {
        "name": "FREE",
        "price": "¥0",
        "unit": "",
        "note": "まずはお試し",
        "features": ["ツール 1日3回まで", "全機能を体験できる", "登録不要"],
        "cta": "いま利用中",
        "highlight": False,
    },
    {
        "name": "STANDARD",
        "price": "¥980",
        "unit": "/月",
        "note": "年払いなら月¥650(34%OFF)",
        "features": ["プロフィール診断 無制限", "全ツール 1日15回", "診断履歴の保存", "アプリ別最適化"],
        "cta": "Standardにする",
        "highlight": True,
    },
    {
        "name": "PREMIUM",
        "price": "¥1,980",
        "unit": "/月",
        "note": "年払いなら月¥1,233(38%OFF)",
        "features": ["全ツール 無制限", "Standardの全機能", "8アプリ別プロフ最適化", "優先サポート"],
        "cta": "Premiumにする",
        "highlight": False,
    },
]

CREDIT_PACKS = [("5回", "¥480"), ("15回", "¥980"), ("50回", "¥2,480")]

USAGE_FILE = os.path.join(os.path.dirname(__file__), "usage.json")


def _today() -> str:
    return time.strftime("%Y-%m-%d")


def _global_usage() -> int:
    try:
        with open(USAGE_FILE, encoding="utf-8") as f:
            data = json.load(f)
        return data.get("count", 0) if data.get("date") == _today() else 0
    except (OSError, json.JSONDecodeError):
        return 0


def _bump_global_usage():
    try:
        with open(USAGE_FILE, "w", encoding="utf-8") as f:
            json.dump({"date": _today(), "count": _global_usage() + 1}, f)
    except OSError:
        pass


def is_paid() -> bool:
    return st.session_state.get("plan", "free") != "free"


def used_today() -> int:
    if st.session_state.get("quota_day") != _today():
        st.session_state["quota_day"] = _today()
        st.session_state["quota_used"] = 0
    return st.session_state.get("quota_used", 0)


def remaining_today() -> int:
    return max(0, FREE_DAILY_LIMIT - used_today())


def paywall():
    st.markdown(
        """
        <div class="hud-panel" style="padding:22px 20px;text-align:center;margin:10px 0 18px;">
          <div style="font-size:1.9rem;">🔒</div>
          <div style="font-size:1.15rem;font-weight:800;margin-top:6px;">本日の無料枠を使い切りました</div>
          <div style="font-size:0.88rem;color:#7b8494;margin-top:8px;line-height:1.7;">
            無料プランは1日3回までです。<br>
            明日また使えるようになります。今すぐ続けたい場合はプランをご確認ください。
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("プランを見る", type="primary", use_container_width=True):
        st.switch_page("views/10_料金プラン.py")


def _log_use(label: str):
    print(
        f"[USE] {time.strftime('%Y-%m-%d %H:%M:%S')} tool={label} "
        f"session_used={st.session_state.get('quota_used', 0)} today_total={_global_usage()}",
        flush=True,
    )


def _check_quota():
    if _global_usage() >= GLOBAL_DAILY_CAP:
        st.warning("本日の提供枠が上限に達しました。申し訳ありませんが、明日またお試しください。")
        st.stop()

    if not is_paid() and used_today() >= FREE_DAILY_LIMIT:
        paywall()
        st.stop()

    st.session_state["quota_used"] = used_today() + 1
    _bump_global_usage()
    _log_use(st.session_state.get("current_tool", "unknown"))


def _call(contents, json_mode: bool):
    _check_quota()
    client = require_client()
    config = types.GenerateContentConfig(response_mime_type="application/json") if json_mode else None

    last_error = None
    for model in MODELS:
        for attempt in range(2):
            try:
                return client.models.generate_content(model=model, contents=contents, config=config)
            except errors.ServerError as e:
                last_error = e
                time.sleep(1.5 * (attempt + 1))
            except errors.ClientError as e:
                if "API_KEY" in str(e):
                    st.error("APIキーが無効です。.env ファイルのキーを確認してください。")
                    st.stop()
                last_error = e
                break

    st.error("AIが混み合っています。少し待ってから、もう一度お試しください。")
    with st.expander("エラー詳細"):
        st.text(str(last_error))
    st.stop()


def ask_json(prompt: str):
    response = _call(
        f"{BASE_PERSONA}\n\n{prompt}\n\n必ず指定されたJSON形式のみを出力してください。",
        json_mode=True,
    )
    try:
        return json.loads(response.text)
    except (json.JSONDecodeError, TypeError):
        st.error("AIの応答を解析できませんでした。もう一度お試しください。")
        with st.expander("エラー詳細"):
            st.text(response.text)
        st.stop()


def ask_json_with_image(prompt: str, image_bytes: bytes, mime_type: str):
    response = _call(
        [
            f"{BASE_PERSONA}\n\n{prompt}\n\n必ず指定されたJSON形式のみを出力してください。",
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
        ],
        json_mode=True,
    )
    try:
        return json.loads(response.text)
    except (json.JSONDecodeError, TypeError):
        st.error("AIの応答を解析できませんでした。もう一度お試しください。")
        st.stop()


def settings_bar() -> dict:
    theme.inject()

    caller = inspect.stack()[1].filename
    st.session_state["current_tool"] = os.path.splitext(os.path.basename(caller))[0]

    if not st.session_state.get("visit_logged"):
        st.session_state["visit_logged"] = True
        print(f"[VISIT] {time.strftime('%Y-%m-%d %H:%M:%S')} 新しい訪問者がアプリを開きました", flush=True)

    current = (
        f"{st.session_state.get('s_gender', '男性')} "
        f"{st.session_state.get('s_age', 32)}歳 · "
        f"{st.session_state.get('s_purpose', list(PURPOSES)[0])} · "
        f"{st.session_state.get('s_app', list(APPS)[0])}"
    )

    if not is_paid():
        left = remaining_today()
        color = "#0fc9a0" if left > 1 else ("#f59f00" if left == 1 else "#ff5c8a")
        st.markdown(
            f"<div style='display:flex;justify-content:flex-end;align-items:center;gap:7px;"
            f"font-size:0.78rem;color:#7b8494;margin:-6px 0 6px;'>"
            f"<span>本日の残り</span>"
            f"<span style='font-weight:800;color:{color};font-size:0.95rem;'>{left}</span>"
            f"<span>/ {FREE_DAILY_LIMIT} 回</span></div>",
            unsafe_allow_html=True,
        )

    with st.expander(f"⚙️ {current}"):
        gender = st.radio("性別", ["男性", "女性", "指定しない"], horizontal=True, key="s_gender")
        age = st.slider("年齢", 18, 60, 32, key="s_age")
        purpose = st.selectbox("目的", list(PURPOSES), key="s_purpose")
        app = st.selectbox("使っているアプリ", list(APPS), key="s_app")
        st.caption(APPS[app])

    gender = st.session_state.get("s_gender", "男性")
    age = st.session_state.get("s_age", 32)
    purpose = st.session_state.get("s_purpose", list(PURPOSES)[0])
    app = st.session_state.get("s_app", list(APPS)[0])

    target = {"男性": "女性", "女性": "男性"}.get(gender, "相手")
    return {
        "gender": gender,
        "target": target,
        "age": age,
        "purpose": purpose,
        "purpose_note": PURPOSES[purpose],
        "app": app,
        "app_note": APPS[app],
    }


def settings_block(s: dict) -> str:
    return f"""【利用者の情報】
- 性別: {s['gender']}({s['age']}歳) / 相手は{s['target']}
- 目的: {s['purpose']} — {s['purpose_note']}
- 使用アプリ: {s['app']} — {s['app_note']}
"""


def score_color(score: int) -> str:
    score = int(score)
    if score >= 80:
        return "#0fc9a0"
    if score >= 60:
        return "#6c5ce7"
    if score >= 40:
        return "#f59f00"
    return "#ff5c8a"


def _gauge_svg(score: int, label: str = "") -> str:
    score = max(0, min(100, int(score)))
    color = score_color(score)
    box, radius = 160, 68
    circumference = 2 * 3.14159265 * radius
    offset = circumference * (1 - score / 100)
    uid = f"g{abs(hash((score, label))) % 1000000}"

    return f"""
    <svg viewBox="0 0 {box} {box}" style="width:100%;height:auto;display:block;">
      <defs>
        <linearGradient id="{uid}" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="{color}"/><stop offset="100%" stop-color="#6c5ce7"/>
        </linearGradient>
        <filter id="{uid}f" x="-60%" y="-60%" width="220%" height="220%">
          <feDropShadow dx="0" dy="3" stdDeviation="4" flood-color="{color}" flood-opacity="0.35"/>
        </filter>
      </defs>
      <circle cx="80" cy="80" r="{radius}" fill="none" stroke="rgba(27,31,42,0.07)" stroke-width="10"/>
      <circle cx="80" cy="80" r="{radius}" fill="none" stroke="url(#{uid})" stroke-width="10"
              stroke-linecap="round" stroke-dasharray="{circumference:.1f}"
              stroke-dashoffset="{offset:.1f}" transform="rotate(-90 80 80)" filter="url(#{uid}f)">
        <animate attributeName="stroke-dashoffset" from="{circumference:.1f}" to="{offset:.1f}"
                 dur="1s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1" keyTimes="0;1"/>
      </circle>
      <text x="80" y="78" text-anchor="middle" dominant-baseline="central" fill="{color}"
            style="font-family:Outfit,sans-serif;font-weight:800;font-size:46px;">{score}</text>
      <text x="80" y="112" text-anchor="middle" fill="#7b8494"
            style="font-family:Outfit,sans-serif;font-weight:600;font-size:12px;letter-spacing:0.2em;">{label}</text>
    </svg>"""


def gauge(score: int, label: str = ""):
    st.markdown(
        f'<div class="hud-panel" style="max-width:190px;margin:0 auto;padding:12px;">'
        f'{_gauge_svg(score, label)}</div>',
        unsafe_allow_html=True,
    )


def big_score(score: int, label: str = ""):
    gauge(score, label)


def score_bars(breakdown: dict):
    rows = ""
    for label, value in breakdown.items():
        value = max(0, min(100, int(value)))
        color = score_color(value)
        rows += f"""
        <div style="margin-bottom:14px;">
          <div style="display:flex;justify-content:space-between;font-size:0.84rem;margin-bottom:6px;
                      color:#4a5263;">
            <span>{label}</span>
            <span style="font-weight:800;color:{color};">{value}</span>
          </div>
          <div style="background:rgba(27,31,42,0.07);border-radius:99px;height:7px;overflow:hidden;">
            <div style="width:{value}%;height:100%;border-radius:99px;
                        background:linear-gradient(90deg,{color},#6c5ce7);
                        box-shadow:0 2px 8px -2px {color}aa;"></div>
          </div>
        </div>"""
    st.markdown(f"<div>{rows}</div>", unsafe_allow_html=True)


def before_after(before: int, after: int):
    before, after = int(before), int(after)
    diff = after - before
    st.markdown(
        f"""
        <div class="hud-panel" style="display:flex;align-items:center;justify-content:center;
                    gap:2vw;padding:14px 8px;margin-bottom:6px;">
          <div style="flex:1;max-width:150px;">{_gauge_svg(before, "BEFORE")}</div>
          <div style="text-align:center;flex:0 0 auto;">
            <div style="font-size:1.25rem;color:#6c5ce7;line-height:1;opacity:0.6;">›››</div>
            <div style="font-weight:800;font-size:1.1rem;margin-top:6px;
                        background:linear-gradient(100deg,#ff5c8a,#6c5ce7);-webkit-background-clip:text;
                        background-clip:text;-webkit-text-fill-color:transparent;">+{diff}</div>
          </div>
          <div style="flex:1;max-width:150px;">{_gauge_svg(after, "AFTER")}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def copyable(text: str):
    st.code(text, language=None, wrap_lines=True)


APP_THEMES = {
    "Pairs": {"bg": "#ffffff", "accent": "#ff6d8a", "header": "#ffffff", "header_text": "#ff6d8a", "label": "Pairs"},
    "タップル": {"bg": "#ffffff", "accent": "#ff8a3d", "header": "#ff8a3d", "header_text": "#ffffff", "label": "tapple"},
    "with": {"bg": "#ffffff", "accent": "#23c16b", "header": "#23c16b", "header_text": "#ffffff", "label": "with"},
    "Tinder": {"bg": "#111318", "accent": "#fe3c72", "header": "#111318", "header_text": "#fe3c72", "label": "tinder"},
    "Bumble": {"bg": "#ffffff", "accent": "#ffc629", "header": "#ffc629", "header_text": "#3b2f00", "label": "bumble"},
    "Omiai": {"bg": "#ffffff", "accent": "#e8546b", "header": "#ffffff", "header_text": "#e8546b", "label": "Omiai"},
    "マリッシュ": {"bg": "#ffffff", "accent": "#f4728c", "header": "#f4728c", "header_text": "#ffffff", "label": "marrish"},
    "東カレデート": {"bg": "#0d0d0d", "accent": "#c8a96a", "header": "#0d0d0d", "header_text": "#c8a96a", "label": "TOKYO CALENDAR"},
    "ブライダルネット": {"bg": "#ffffff", "accent": "#e35d7a", "header": "#ffffff", "header_text": "#e35d7a", "label": "ブライダルネット"},
}


def app_preview(app: str, text: str, age: int, area: str = ""):
    theme = APP_THEMES.get(app, APP_THEMES["Pairs"])
    dark = app in ("Tinder", "東カレデート")
    body_color = "#f2f2f2" if dark else "#333333"
    sub_color = "#999999" if dark else "#888888"
    card_bg = "#1c1f26" if dark else "#fafafa"
    safe = (
        text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
    )
    meta = f"{age}歳" + (f" · {area}" if area else "")

    st.markdown(
        f"""
        <div style="width:100%;max-width:320px;margin:0 auto;border:9px solid #1a1f2e;border-radius:30px;
                    overflow:hidden;background:{theme['bg']};
                    box-shadow:0 10px 40px -10px rgba(0,229,255,0.35),0 0 0 1px rgba(255,255,255,0.06);">
          <div style="background:{theme['header']};color:{theme['header_text']};padding:10px 14px;
                      font-weight:700;font-size:0.9rem;text-align:center;letter-spacing:0.05em;">
            {theme['label']}
          </div>
          <div style="height:150px;background:linear-gradient(135deg,{theme['accent']}33,{theme['accent']}0a);
                      display:flex;align-items:center;justify-content:center;color:{sub_color};font-size:0.8rem;">
            プロフィール写真
          </div>
          <div style="padding:14px;">
            <div style="font-weight:700;font-size:1.05rem;color:{body_color};">{meta}</div>
            <div style="height:2px;width:34px;background:{theme['accent']};margin:8px 0 12px;"></div>
            <div style="background:{card_bg};border-radius:10px;padding:12px;font-size:0.83rem;
                        line-height:1.75;color:{body_color};max-height:260px;overflow-y:auto;">
              {safe}
            </div>
            <div style="margin-top:14px;text-align:center;">
              <span style="display:inline-block;background:{theme['accent']};color:#fff;border-radius:99px;
                           padding:8px 28px;font-size:0.85rem;font-weight:700;">いいね</span>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


HISTORY_FILE = os.path.join(os.path.dirname(__file__), "history.json")


def load_history() -> list:
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def save_history(kind: str, summary: str, score=None, detail: str = ""):
    history = load_history()
    history.insert(
        0,
        {
            "kind": kind,
            "summary": summary[:120],
            "score": score,
            "detail": detail,
            "at": time.strftime("%Y-%m-%d %H:%M"),
        },
    )
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history[:100], f, ensure_ascii=False, indent=2)
    except OSError:
        pass
