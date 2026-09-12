import streamlit as st

st.set_page_config(page_title="婚活AIコーチ", page_icon="💌", layout="centered")

PAGES = {
    "": [st.Page("views/0_ホーム.py", title="ホーム", icon="🏠", default=True)],
    "プロフィールを整える": [
        st.Page("views/1_プロフィール診断.py", title="プロフィール診断", icon="💌"),
        st.Page("views/7_写真診断.py", title="スクショ診断", icon="📷"),
        st.Page("views/2_プロフィール作成.py", title="プロフィール作成", icon="✍️"),
    ],
    "やり取りを進める": [
        st.Page("views/4_初回メッセージ.py", title="初回メッセージ", icon="📩"),
        st.Page("views/3_返信AI.py", title="返信AI", icon="💬"),
        st.Page("views/6_会話シミュレーション.py", title="会話シミュレーション", icon="🎮"),
    ],
    "会う準備をする": [
        st.Page("views/5_デートプラン.py", title="デートプラン", icon="🗓"),
        st.Page("views/8_スタイル診断.py", title="スタイル診断", icon="👔"),
    ],
    "その他": [
        st.Page("views/9_履歴.py", title="診断履歴", icon="📚"),
        st.Page("views/10_料金プラン.py", title="料金プラン", icon="💎"),
    ],
}

st.navigation(PAGES).run()
