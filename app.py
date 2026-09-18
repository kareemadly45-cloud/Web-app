import streamlit as st
from utils import CATEGORIES, init_db, is_admin, logout_admin, hide_streamlit_ui

# ============================================
st.set_page_config(page_title="La Mariposa", page_icon="🦋", layout="wide")
hide_streamlit_ui()
init_db()

# ============================================
# CSS
# ============================================
st.markdown("""
<style>
    .hero {
        padding: 80px 30px;
        text-align: center;
        background: linear-gradient(135deg, #1a1a1a 0%, #4a4a4a 100%);
        color: white;
        border-radius: 18px;
        margin-bottom: 40px;
    }
    .hero h1 { font-size: 48px; margin-bottom: 10px; font-weight: 700; letter-spacing: 2px; }
    .hero p { font-size: 20px; opacity: 0.85; color: #F39C12; }

    .section-title {
        font-size: 32px;
        font-weight: 700;
        text-align: center;
        margin-bottom: 40px;
        margin-top: 30px;
    }

    .category-card {
        background: #1a1a1a;
        border: 2px solid #800020;
        border-radius: 22px;
        padding: 40px 20px 25px;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(128,0,32,0.3);
    }
    .category-card:hover {
        border-color: #F39C12;
        box-shadow: 0 12px 35px rgba(243,156,18,0.3);
        transform: translateY(-5px);
    }
    .category-icon { font-size: 80px; margin-bottom: 15px; }
    .category-name {
        font-size: 24px;
        font-weight: 700;
        letter-spacing: 1.5px;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# Top Bar
# ============================================
col1, col2 = st.columns([5, 1])
with col1:
    st.markdown('<div style="font-size:30px;font-weight:800;letter-spacing:3px;">LA MARIPOSA <span style="color:#800020;">STORE</span></div>', unsafe_allow_html=True)
with col2:
    if is_admin():
        if st.button("🚪 Logout", key="top_logout", use_container_width=True):
            logout_admin()
            st.rerun()
    else:
        if st.button("🔐 Admin", key="top_admin", use_container_width=True):
            st.switch_page("pages/5_Admin.py")

st.markdown('<hr style="border:none;border-top:1px solid #333;margin:10px 0 20px;">', unsafe_allow_html=True)

# ============================================
# Hero
# ============================================
st.markdown("""
<div class="hero">
    <h1>LA MARIPOSA STORE</h1>
    <p>✨ Premium Collection ✨</p>
</div>
""", unsafe_allow_html=True)

# ============================================
# Categories
# ============================================
st.markdown('<div class="section-title">Shop by Category</div>', unsafe_allow_html=True)

cols = st.columns(len(CATEGORIES))
for col, (slug, cat) in zip(cols, CATEGORIES.items()):
    with col:
        st.markdown(f"""
        <div class="category-card">
            <div class="category-icon">{cat['icon']}</div>
            <div class="category-name">{cat['name'].upper()}</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button(f"Enter {cat['name']}", key=f"btn_{slug}", use_container_width=True):
            st.switch_page(f"pages/{cat['page']}.py")

# ============================================
# Footer
# ============================================
st.markdown("---")
st.markdown('<div style="text-align:center;padding:20px;color:#999;letter-spacing:2px;">© 2026 LA MARIPOSA STORE</div>', unsafe_allow_html=True)
