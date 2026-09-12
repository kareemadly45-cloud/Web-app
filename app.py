import streamlit as st
from utils import (
    CATEGORIES, init_db, get_whatsapp_link,
    is_admin, login_admin, logout_admin
)

# ============================================
st.set_page_config(page_title="La Mariposa", page_icon="💎", layout="wide")
init_db()

# ============================================
# 🔐 فحص الرابط السري
# ============================================
query_params = st.query_params
admin_access = query_params.get("admin") == "1"

# ============================================
# CSS — Black Theme + نبيتي
# ============================================
st.markdown("""
<style>
    [data-testid="stSidebar"] { display: none; }
    [data-testid="collapsedControl"] { display: none; }

    .stApp { background: #0a0a0a !important; }
    section.main { background: #0a0a0a !important; }
    .main { padding-top: 0rem; }
    html, body, [class*="css"] { color: #f0f0f0; }

    .top-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 20px 35px;
        background: linear-gradient(135deg, #1a0000 0%, #2c0000 100%);
        border: 2px solid #800020;
        border-radius: 18px;
        margin-bottom: 30px;
        box-shadow: 0 8px 40px rgba(128,0,32,0.5);
    }
    .logo {
        font-size: 32px;
        font-weight: 800;
        letter-spacing: 4px;
        color: white;
    }
    .logo span {
        color: #800020;
        text-shadow: 0 0 25px rgba(128,0,32,0.9), 0 0 50px rgba(128,0,32,0.5);
    }

    .hero {
        padding: 90px 30px;
        text-align: center;
        background: linear-gradient(135deg, #1a0000 0%, #000000 100%);
        border: 2px solid #800020;
        color: white;
        border-radius: 25px;
        margin-bottom: 50px;
        box-shadow: 0 20px 60px rgba(128,0,32,0.4);
        position: relative;
        overflow: hidden;
    }
    .hero::before {
        content: "";
        position: absolute;
        top: -50%; left: -50%;
        width: 200%; height: 200%;
        background: radial-gradient(circle, rgba(128,0,32,0.15) 0%, transparent 70%);
        animation: pulse 4s ease-in-out infinite;
    }
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 0.5; }
        50% { transform: scale(1.1); opacity: 0.8; }
    }
    .hero h1 {
        font-size: 58px;
        margin-bottom: 15px;
        font-weight: 800;
        letter-spacing: 4px;
        position: relative;
        z-index: 2;
        text-shadow: 0 5px 30px rgba(0,0,0,0.8);
    }
    .hero h1 span {
        color: #800020;
        text-shadow: 0 0 30px rgba(128,0,32,1), 0 0 60px rgba(128,0,32,0.6);
    }
    .hero p {
        font-size: 24px;
        opacity: 0.95;
        position: relative;
        z-index: 2;
        color: #F39C12;
        letter-spacing: 3px;
    }

    .section-title {
        font-size: 36px;
        font-weight: 800;
        text-align: center;
        margin-bottom: 50px;
        margin-top: 40px;
        background: linear-gradient(135deg, #800020, #d4a5a5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: 3px;
    }

    .cat-card-1, .cat-card-2, .cat-card-3, .cat-card-4 {
        border-radius: 25px;
        padding: 45px 20px 35px;
        text-align: center;
        transition: all 0.35s ease;
        box-shadow: 0 10px 30px rgba(0,0,0,0.6);
    }
    .cat-card-1 { background: linear-gradient(135deg, #2a0a0a 0%, #4a1010 100%); border: 3px solid #FF6B6B; }
    .cat-card-2 { background: linear-gradient(135deg, #1a0a2a 0%, #2a104a 100%); border: 3px solid #9B59B6; }
    .cat-card-3 { background: linear-gradient(135deg, #0a1a2a 0%, #102a4a 100%); border: 3px solid #3498DB; }
    .cat-card-4 { background: linear-gradient(135deg, #2a1a0a 0%, #4a2a10 100%); border: 3px solid #E74C3C; }

    .cat-card-1:hover, .cat-card-2:hover, .cat-card-3:hover, .cat-card-4:hover {
        transform: translateY(-12px) scale(1.03);
        box-shadow: 0 25px 60px rgba(128,0,32,0.6);
    }
    .category-img {
        width: 130px;
        height: 130px;
        object-fit: contain;
        margin-bottom: 22px;
        transition: 0.35s;
        filter: drop-shadow(0 6px 15px rgba(255,255,255,0.2));
    }
    .cat-card-1:hover .category-img,
    .cat-card-2:hover .category-img,
    .cat-card-3:hover .category-img,
    .cat-card-4:hover .category-img {
        transform: scale(1.18) rotate(-6deg);
        filter: drop-shadow(0 10px 25px rgba(128,0,32,0.8));
    }
    .category-name {
        font-size: 28px;
        font-weight: 800;
        letter-spacing: 3px;
        color: #ffffff;
    }

    .stButton > button {
        border-radius: 12px;
        font-weight: 700;
        transition: 0.25s;
        border: 2px solid #800020;
        background: #1a1a1a;
        color: #ffffff;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #800020, #B22234);
        color: white;
        border-color: #800020;
        transform: translateY(-2px);
        box-shadow: 0 10px 30px rgba(128,0,32,0.7);
    }

    .whatsapp-section {
        text-align: center;
        padding: 50px 20px;
        background: linear-gradient(135deg, #0a2a1a 0%, #0a3a2a 100%);
        border: 2px solid #25D366;
        border-radius: 25px;
        margin-top: 40px;
        box-shadow: 0 10px 40px rgba(37,211,102,0.3);
    }
    .whatsapp-section h2 {
        color: #25D366;
        font-size: 34px;
        font-weight: 800;
        margin-bottom: 15px;
        text-shadow: 0 0 20px rgba(37,211,102,0.6);
    }
    .whatsapp-section p {
        color: #d0d0d0;
        font-size: 18px;
        margin-bottom: 25px;
    }
    .whatsapp-btn {
        display: inline-block;
        background: linear-gradient(135deg, #25D366, #128C7E);
        color: white !important;
        padding: 18px 45px;
        border-radius: 50px;
        font-size: 20px;
        font-weight: 700;
        text-decoration: none !important;
        box-shadow: 0 10px 30px rgba(37,211,102,0.5);
        transition: 0.3s;
        margin: 20px 0;
    }
    .whatsapp-btn:hover {
        transform: translateY(-4px);
        box-shadow: 0 15px 50px rgba(37,211,102,0.8);
    }

    .footer {
        text-align: center;
        padding: 35px 20px;
        color: #666;
        letter-spacing: 3px;
        font-weight: 600;
        margin-top: 40px;
        border-top: 2px solid #800020;
    }

    .stMarkdown, .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #f0f0f0;
    }
    hr { border-color: #800020 !important; opacity: 0.4; }

    /* ====== Admin Panel Style ====== */
    .admin-box {
        background: linear-gradient(135deg, #1a0000 0%, #2c0000 100%);
        border: 2px solid #800020;
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 15px 50px rgba(128,0,32,0.5);
        margin-top: 30px;
    }
    .stat-box {
        background: linear-gradient(135deg, #1a0000 0%, #2c0000 100%);
        border: 2px solid #800020;
        color: white;
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 15px;
    }
    .stat-box h3 {
        margin: 10px 0 5px;
        font-size: 38px;
        color: #800020;
        text-shadow: 0 0 20px rgba(128,0,32,0.8);
    }
    .stat-box p {
        margin: 0;
        font-size: 14px;
        opacity: 0.8;
        letter-spacing: 2px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# 🔐 لو المستخدم داخل على الرابط السري
# ============================================
if admin_access:
    st.markdown("""
    <div style="text-align:center; padding:30px 0;">
        <h1 style="letter-spacing:5px; color:#800020; text-shadow: 0 0 30px rgba(128,0,32,0.7);">🔐 ADMIN PANEL</h1>
        <p style="color:#F39C12; letter-spacing:3px;">La Mariposa STORE</p>
    </div>
    """, unsafe_allow_html=True)

    # لو مش مسجل دخول → فورم الباسورد
    if not is_admin():
        st.markdown('<div class="admin-box">', unsafe_allow_html=True)
        st.subheader("🔑 Login Required")
        st.write("ادخل الباسورد للدخول على لوحة التحكم")

        with st.form("admin_login_form"):
            pwd = st.text_input("Password", type="password", placeholder="••••••••")
            submit = st.form_submit_button("🔓 Login", use_container_width=True)

            if submit:
                if login_admin(pwd):
                    st.success("✅ Welcome Admin!")
                    st.rerun()
                else:
                    st.error("❌ Wrong password")

        st.markdown('</div>', unsafe_allow_html=True)

    # لو مسجل دخول → لوحة التحكم
    else:
        st.success("✅ مسجل دخول كـ Admin")

        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("🚪 Logout", use_container_width=True):
                logout_admin()
                st.rerun()

        st.markdown("---")
        st.markdown("### 📊 Statistics")

        from utils import get_products
        total = 0
        cols = st.columns(len(CATEGORIES))
        for col, (slug, cat) in zip(cols, CATEGORIES.items()):
            count = len(get_products(slug))
            total += count
            with col:
                st.markdown(f"""
                <div class="stat-box">
                    <div style="font-size:40px;">{cat['icon']}</div>
                    <h3>{count}</h3>
                    <p>{cat['name'].upper()}</p>
                </div>
                """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="text-align:center; padding:25px; background:linear-gradient(135deg,#1a0000,#2c0000); border:2px solid #800020; border-radius:15px; margin-top:20px;">
            <div style="font-size:16px; color:#999; letter-spacing:2px;">TOTAL PRODUCTS</div>
            <div style="font-size:48px; font-weight:800; color:#800020; text-shadow: 0 0 30px rgba(128,0,32,0.8);">{total}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 🚀 روابط سريعة للكاتيجوري")

        cols = st.columns(len(CATEGORIES))
        for col, (slug, cat) in zip(cols, CATEGORIES.items()):
            with col:
                if st.button(f"{cat['icon']} {cat['name']}",
                             key=f"goto_{slug}",
                             use_container_width=True):
                    st.switch_page(f"pages/{cat['page']}.py")

        st.markdown("---")
        st.info("""
        **ملاحظة:** بعد ما تدخل على أي كاتيجوري هتلاقي فورم **➕ Add New Product** ظاهر تلقائي
        وفوق كل منتج زرار **✏️ Edit** و **🗑️ Delete**.
        """)

    # زر الرجوع
    st.markdown("---")
    if st.button("⬅️ الرجوع للصفحة الرئيسية", use_container_width=True):
        st.query_params.clear()
        st.rerun()

    # ⛔ وقف هنا — مش هنعرض الموقع العادي
    st.stop()

# ============================================
# 🏠 الموقع العادي (لما مفيش admin=1)
# ============================================

# Header
st.markdown("""
<div class="top-header">
    <div class="logo">La Mariposa <span>STORE</span></div>
    <div style="color:#F39C12; font-size:18px; font-weight:600;">✨ Premium Collection ✨</div>
</div>
""", unsafe_allow_html=True)

# Hero
st.markdown("""
<div class="hero">
    <h1>La Mariposa <span>STORE</span></h1>
    <p>✨ Premium Collection ✨</p>
</div>
""", unsafe_allow_html=True)

# Categories
st.markdown('<div class="section-title">Shop by Category</div>', unsafe_allow_html=True)

cat_list = list(CATEGORIES.items())
cols = st.columns(len(cat_list))

for i, (col, (slug, cat)) in enumerate(zip(cols, cat_list), start=1):
    with col:
        st.markdown(f"""
        <div class="cat-card-{i}">
            <img src="{cat['image']}" class="category-img">
            <div class="category-name">{cat['name'].upper()}</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button(f"Enter {cat['name']}", key=f"btn_{slug}", use_container_width=True):
            st.switch_page(f"pages/{cat['page']}.py")

# WhatsApp Section
st.markdown("---")
st.markdown("""
<div class="whatsapp-section">
    <h2>💬 تواصل معنا على واتساب</h2>
    <p>اضغط على الزر وهتتواصل معنا مباشرة مع رسالة جاهزة</p>
</div>
""", unsafe_allow_html=True)

col_l, col_c, col_r = st.columns([1, 2, 1])
with col_c:
    wa_link = get_whatsapp_link()
    st.markdown(f'''
    <a href="{wa_link}" target="_blank" class="whatsapp-btn" style="display:block; text-align:center;">
        📱 WhatsApp Us Now
    </a>
    ''', unsafe_allow_html=True)

# Footer
st.markdown(
    '<div class="footer">© 2026 La Mariposa STORE — ALL RIGHTS RESERVED</div>',
    unsafe_allow_html=True
)
st.markdown("""
<style>
    /* إخفاء الـ Header بالكامل */
    header[data-testid="stHeader"] { display: none !important; }
    
    /* إخفاء الـ Toolbar */
    [data-testid="stToolbar"] { display: none !important; }
    
    /* إخفاء زر Deploy */
    .stDeployButton { display: none !important; }
    
    /* إخفاء القايمة الرئيسية */
    #MainMenu { visibility: hidden !important; }
    
    /* إخفاء الـ Footer */
    footer { visibility: hidden !important; }
    
    /* إخفاء الـ Decoration (الشريط الملون فوق) */
    [data-testid="stDecoration"] { display: none !important; }
    
    /* إخفاء Manage app button */
    [data-testid="manage-app-button"] { display: none !important; }
    
    /* إخفاء Share button */
    [data-testid="stAppDeployButton"] { display: none !important; }
</style>
""", unsafe_allow_html=True)
