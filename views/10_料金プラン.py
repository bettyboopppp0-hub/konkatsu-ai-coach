import streamlit as st

from core import CREDIT_PACKS, FREE_DAILY_LIMIT, PLANS, remaining_today, settings_bar

st.title("料金プラン")
st.caption("無料でも1日3回使えます。もっと使いたくなったときだけ、プランをご検討ください。")

settings_bar()

st.markdown(
    f"""
    <div class="hud-panel" style="padding:14px 18px;margin-bottom:18px;text-align:center;">
      <span style="font-size:0.85rem;color:#7b8494;">本日の残り回数</span>
      <span style="font-size:1.25rem;font-weight:800;margin-left:8px;
                   background:linear-gradient(100deg,#ff5c8a,#6c5ce7);-webkit-background-clip:text;
                   background-clip:text;-webkit-text-fill-color:transparent;">
        {remaining_today()} / {FREE_DAILY_LIMIT}
      </span>
    </div>
    """,
    unsafe_allow_html=True,
)

for plan in PLANS:
    border = "2px solid transparent" if plan["highlight"] else "1px solid rgba(27,31,42,0.08)"
    bg = (
        "background:linear-gradient(#fff,#fff) padding-box,"
        "linear-gradient(100deg,#ff5c8a,#6c5ce7) border-box;"
        if plan["highlight"]
        else "background:rgba(255,255,255,0.78);"
    )
    badge = (
        "<div style='position:absolute;top:-11px;left:50%;transform:translateX(-50%);"
        "background:linear-gradient(100deg,#ff5c8a,#6c5ce7);color:#fff;font-size:0.7rem;"
        "font-weight:800;padding:3px 14px;border-radius:99px;white-space:nowrap;'>一番人気</div>"
        if plan["highlight"]
        else ""
    )
    features = "".join(
        f"<div style='font-size:0.86rem;color:#4a5263;padding:5px 0;'>✓&nbsp;&nbsp;{f}</div>"
        for f in plan["features"]
    )

    st.markdown(
        f"""
        <div style="position:relative;border:{border};{bg}border-radius:20px;
                    padding:22px 20px 16px;margin-bottom:14px;
                    box-shadow:0 6px 28px -10px rgba(80,60,180,0.2);">
          {badge}
          <div style="font-size:0.76rem;font-weight:800;letter-spacing:0.14em;color:#7b8494;">{plan['name']}</div>
          <div style="margin:6px 0 2px;">
            <span style="font-size:2.1rem;font-weight:800;">{plan['price']}</span>
            <span style="font-size:0.9rem;color:#7b8494;">{plan['unit']}</span>
          </div>
          <div style="font-size:0.78rem;color:#7b8494;margin-bottom:12px;">{plan['note']}</div>
          <div style="border-top:1px solid rgba(27,31,42,0.07);padding-top:10px;">{features}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if plan["name"] != "FREE":
        st.button(plan["cta"], key=plan["name"], type="primary" if plan["highlight"] else "secondary", use_container_width=True)

st.markdown("#### 買い切りのクレジットパック")
st.caption("月額が不要な方は、必要な分だけ購入できます。")

cols = st.columns(len(CREDIT_PACKS))
for col, (count, price) in zip(cols, CREDIT_PACKS):
    with col:
        st.markdown(
            f"""
            <div class="hud-panel" style="padding:16px 10px;text-align:center;">
              <div style="font-size:0.95rem;font-weight:700;">{count}</div>
              <div style="font-size:1.2rem;font-weight:800;margin-top:4px;
                          background:linear-gradient(100deg,#ff5c8a,#6c5ce7);-webkit-background-clip:text;
                          background-clip:text;-webkit-text-fill-color:transparent;">{price}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.info("💳 決済機能はまだ準備中です。現在はすべての機能を無料枠の範囲でお試しいただけます。")
