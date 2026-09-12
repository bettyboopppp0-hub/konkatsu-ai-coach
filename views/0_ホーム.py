import streamlit as st

from core import load_history, settings_bar

st.title("婚活AIコーチ")
st.caption("いま困っていることを選んでください。最適なツールに案内します。")

settings_bar()

WORRIES = [
    ("いいねが来ない", "プロフィールをAIが採点して、相手目線の本音まで教えます", "views/1_プロフィール診断.py", "💌"),
    ("写真に自信がない", "写真を撮り直すべきか、次に何を撮るべきかを指示します", "views/7_写真診断.py", "📷"),
    ("何を書けばいいか分からない", "選ぶだけでプロフィールをゼロから作ります", "views/2_プロフィール作成.py", "✍️"),
    ("最初の一通が送れない", "相手のプロフを読み解いて、返事が来る一通を作ります", "views/4_初回メッセージ.py", "📩"),
    ("会話が続かない", "相手の温度感を読んで、返信を3パターン作ります", "views/3_返信AI.py", "💬"),
    ("会話の練習がしたい", "AIが相手役に。好感度の上下を見ながら練習できます", "views/6_会話シミュレーション.py", "🎮"),
    ("デートに誘いたい", "エリアと予算からプランと誘い文句を作ります", "views/5_デートプラン.py", "🗓"),
    ("服装が分からない", "写真または条件から、具体的なコーデを指定します", "views/8_スタイル診断.py", "👔"),
]

st.markdown('<div class="worry-grid">', unsafe_allow_html=True)
for title, desc, page, icon in WORRIES:
    if st.button(f"{icon}  **{title}**  \n{desc}", key=page, use_container_width=True):
        st.switch_page(page)
st.markdown("</div>", unsafe_allow_html=True)

history = load_history()
if history:
    st.divider()
    st.markdown("#### 最近の診断")
    for item in history[:3]:
        score = f" — {item['score']}点" if item.get("score") is not None else ""
        st.markdown(f"`{item['at']}` **{item['kind']}**{score}")
    if st.button("履歴をすべて見る"):
        st.switch_page("views/9_履歴.py")
