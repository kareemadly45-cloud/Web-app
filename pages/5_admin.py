import streamlit as st
from utils import (
    is_admin, login_admin, logout_admin,
    CATEGORIES, get_products, hide_streamlit_ui
)

st.set_page_config(page_title="Admin - La Mariposa", page_icon="🔐", layout="centered")
hide_streamlit_ui()

st.markdown("""
<style>
    .stat-box {
        background: linear-gradient(135deg, #800020 0%, #4a0010 100%);
        color: white;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
    }
    .stat-box h3 { margin: 0; font-size: 32px; color: #F39C12; }
    .stat-box p { margin: 5px 0 0; font-size: 14px; opacity: 0.9; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center;padding:20px 0;">
    <h1 style="letter-spacing:3px;">🔐 ADMIN PANEL</h1>
    <p style="color:#999;">La Mariposa Control Center</p>
</div>
""", unsafe_allow_html=True)

if not is_admin():
    st.subheader("🔑 Login Required")
    with st.form("admin_login_form"):
        pwd = st.text_input("Password", type="password", placeholder="••••••••")
        submit = st.form_submit_button("🔓 Login", use_container_width=True)
        if submit:
            if login_admin(pwd):
                st.success("✅ Welcome Admin!")
                st.rerun()
            else:
                st.error("❌ Wrong password")
else:
    st.success("✅ انت مسجل دخول كـ Admin")

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("🚪 Logout", use_container_width=True):
            logout_admin()
            st.rerun()

    st.markdown("---")
    st.subheader("📊 Statistics")

    total = 0
    cols = st.columns(len(CATEGORIES))
    for col, (slug, cat) in zip(cols, CATEGORIES.items()):
        count = len(get_products(slug))
        total += count
        with col:
            st.markdown(f"""
            <div class="stat-box">
                <div style="font-size:30px;">{cat['icon']}</div>
                <h3>{count}</h3>
                <p>{cat['name'].upper()}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="text-align:center;padding:20px;background:#1a1a1a;border-radius:12px;margin-top:10px;">
        <div style="font-size:16px;color:#999;">Total Products</div>
        <div style="font-size:36px;font-weight:800;color:#F39C12;">{total}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("🚀 روابط سريعة")

    cols = st.columns(len(CATEGORIES))
    for col, (slug, cat) in zip(cols, CATEGORIES.items()):
        with col:
            if st.button(f"{cat['icon']} {cat['name']}", key=f"goto_{slug}", use_container_width=True):
                st.switch_page(f"pages/{cat['page']}.py")

st.markdown("---")
if st.button("⬅️ Back to Home", use_container_width=True):
    st.switch_page("app.py")
