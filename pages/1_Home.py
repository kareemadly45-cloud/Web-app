import streamlit as st
import uuid
from utils import (
    get_products, add_product, update_product, delete_product,
    render_product_card, calc_discount,
    is_admin, login_admin, logout_admin,
    save_uploaded_image
)

# ============================================
CATEGORY_SLUG = "home"
CATEGORY_NAME = "Home"
CATEGORY_ICON = "🏠"
# ============================================

st.set_page_config(page_title=f"{CATEGORY_NAME} - La Mariposa",
                   page_icon=CATEGORY_ICON, layout="wide")

# إخفاء Sidebar
st.markdown("""
<style>
    [data-testid="stSidebar"] { display: none; }
    [data-testid="collapsedControl"] { display: none; }
</style>
""", unsafe_allow_html=True)

admin_mode = is_admin()

# ============================================
# Header
# ============================================
col1, col2 = st.columns([5, 1])
with col1:
    st.markdown(f'<div style="font-size:26px; font-weight:700;">{CATEGORY_ICON} {CATEGORY_NAME}</div>',
                unsafe_allow_html=True)
with col2:
    if admin_mode:
        if st.button("🚪 Logout", key=f"logout_{CATEGORY_SLUG}", use_container_width=True):
            logout_admin()
            st.rerun()

if st.button("⬅️ Back to Home"):
    st.switch_page("app.py")

st.markdown("---")

# ============================================
# 🟢 Add Product (Admin Only) — مع File Uploader
# ============================================
if admin_mode:
    with st.expander("➕ Add New Product", expanded=False):
        with st.form(f"add_form_{CATEGORY_SLUG}", clear_on_submit=True):
            name = st.text_input("Product Name")
            desc = st.text_area("Description")
            
            col1, col2 = st.columns(2)
            with col1:
                price = st.number_input("Price (EGP)", min_value=0.0, value=0.0, step=50.0)
            with col2:
                has_disc = st.checkbox("Has Discount?")
            
            price_after = st.number_input(
                "Price After Discount (EGP)",
                min_value=0.0,
                value=0.0,
                step=50.0
            ) if has_disc else 0.0

            # 🖼️ رفع صورة من الجهاز
            uploaded = st.file_uploader(
                "📷 ارفع صورة المنتج",
                type=["png", "jpg", "jpeg", "webp"]
            )

            if st.form_submit_button("➕ Add Product", use_container_width=True):
                if not name or price <= 0:
                    st.error("Name and Price are required.")
                else:
                    # حفظ الصورة لو موجودة
                    img_path = save_uploaded_image(uploaded) if uploaded else ""
                    
                    add_product(CATEGORY_SLUG, {
                        "id": str(uuid.uuid4()),
                        "name": name,
                        "description": desc,
                        "price": price,
                        "price_after": price_after if has_disc else 0,
                        "image": img_path,
                    })
                    st.success(f"✅ '{name}' added!")
                    st.rerun()

# ============================================
# Products Grid
# ============================================
products = get_products(CATEGORY_SLUG)
st.markdown(f"### All {CATEGORY_NAME} ({len(products)})")

if not products:
    st.info("لا توجد منتجات بعد.")
    if not admin_mode:
        st.caption("👈 لو انت الأدمن، سجّل دخول من صفحة Admin.")
else:
    cols = st.columns(3)
    for idx, product in enumerate(products):
        with cols[idx % 3]:
            render_product_card(product)

            if admin_mode:
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("✏️ Edit", key=f"edit_{product['id']}", use_container_width=True):
                        st.session_state[f"editing_{product['id']}"] = True
                        st.rerun()
                with c2:
                    if st.button("🗑️ Delete", key=f"del_{product['id']}", use_container_width=True):
                        delete_product(CATEGORY_SLUG, product["id"])
                        st.rerun()
            else:
                if st.button("👁️ Details", key=f"view_{product['id']}", use_container_width=True):
                    st.session_state["view_product"] = product
                    st.rerun()

            # ============================================
            # Edit Form
            # ============================================
            if admin_mode and st.session_state.get(f"editing_{product['id']}"):
                with st.form(f"edit_form_{product['id']}"):
                    st.write(f"**Editing: {product['name']}**")
                    name = st.text_input("Name", value=product["name"])
                    desc = st.text_area("Description", value=product.get("description", ""))
                    price = st.number_input("Price", value=float(product.get("price", 0)), min_value=0.0)
                    has_disc = st.checkbox("Has Discount", value=bool(product.get("price_after", 0)))
                    price_after = st.number_input(
                        "Price After Discount",
                        value=float(product.get("price_after", 0)),
                        min_value=0.0
                    ) if has_disc else 0.0

                    # 🖼️ رفع صورة جديدة (اختياري)
                    uploaded = st.file_uploader(
                        "📷 ارفع صورة جديدة (اختياري)",
                        type=["png", "jpg", "jpeg", "webp"],
                        key=f"upload_{product['id']}"
                    )

                    if product.get("image"):
                        st.caption("الصورة الحالية:")
                        st.image(product["image"], width=120)

                    cc1, cc2 = st.columns(2)
                    if cc1.form_submit_button("💾 Save", use_container_width=True):
                        # لو رفع صورة جديدة، استخدمها — غير كده استخدم القديمة
                        img_path = save_uploaded_image(uploaded) if uploaded else product.get("image", "")
                        
                        update_product(CATEGORY_SLUG, product["id"], {
                            "id": product["id"],
                            "name": name,
                            "description": desc,
                            "price": price,
                            "price_after": price_after if has_disc else 0,
                            "image": img_path,
                        })
                        st.session_state[f"editing_{product['id']}"] = False
                        st.rerun()
                    
                    if cc2.form_submit_button("❌ Cancel", use_container_width=True):
                        st.session_state[f"editing_{product['id']}"] = False
                        st.rerun()

# ============================================
# Details Modal
# ============================================
if st.session_state.get("view_product"):
    p = st.session_state["view_product"]
    st.markdown("---")
    st.markdown(f"### 👁️ {p['name']}")
    cc1, cc2 = st.columns([1, 2])
    with cc1:
        if p.get("image"):
            st.image(p["image"], use_container_width=True)
    with cc2:
        st.write(p.get("description", ""))
        price, price_after = p.get("price", 0), p.get("price_after", 0)
        if price_after and price_after < price:
            st.markdown(f"~~{price:.0f} EGP~~ → **{price_after:.0f} EGP**")
        else:
            st.markdown(f"**{price:.0f} EGP**")
    if st.button("❌ Close"):
        st.session_state["view_product"] = None
        st.rerun()
