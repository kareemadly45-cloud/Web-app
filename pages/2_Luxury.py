import streamlit as st
import uuid
from utils import (
    get_products, add_product, update_product, delete_product,
    render_product_card, is_admin, logout_admin, save_uploaded_image,
    hide_streamlit_ui, calc_discount, get_whatsapp_link
)

# ============================================
CATEGORY_SLUG = "luxury"
CATEGORY_NAME = "Luxury"
CATEGORY_ICON = "💎"
# ============================================

st.set_page_config(
    page_title=f"{CATEGORY_NAME} - La Mariposa",
    page_icon=CATEGORY_ICON,
    layout="wide"
)
hide_streamlit_ui()

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
    st.markdown(
        f'<div style="font-size:26px; font-weight:700;">{CATEGORY_ICON} {CATEGORY_NAME}</div>',
        unsafe_allow_html=True
    )
with col2:
    if admin_mode:
        if st.button("🚪 Logout", key=f"logout_{CATEGORY_SLUG}", use_container_width=True):
            logout_admin()
            st.rerun()

if st.button("⬅️ Back to Home"):
    st.switch_page("app.py")

st.markdown("---")

# ============================================
# 🟢 Add Product (Admin Only)
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

            if has_disc:
                price_after = st.number_input(
                    "Price After Discount (EGP)",
                    min_value=0.0,
                    value=0.0,
                    step=50.0
                )
            else:
                price_after = 0.0

            # 🖼️ رفع صور متعددة
            uploaded_files = st.file_uploader(
                "📷 ارفع صور المنتج (يمكن اختيار أكثر من صورة)",
                type=["png", "jpg", "jpeg", "webp"],
                accept_multiple_files=True,
                key=f"upload_{CATEGORY_SLUG}"
            )

            if st.form_submit_button("➕ Add Product", use_container_width=True):
                if not name or price <= 0:
                    st.error("Name and Price are required.")
                else:
                    product_id = str(uuid.uuid4())

                    image_paths = []
                    if uploaded_files:
                        for f in uploaded_files:
                            p = save_uploaded_image(f, product_id)
                            if p:
                                image_paths.append(p)

                    add_product(CATEGORY_SLUG, {
                        "id": product_id,
                        "name": name,
                        "description": desc,
                        "price": price,
                        "price_after": price_after if has_disc else 0,
                        "images": image_paths,
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

                    if has_disc:
                        price_after = st.number_input(
                            "Price After Discount",
                            value=float(product.get("price_after", 0)),
                            min_value=0.0
                        )
                    else:
                        price_after = 0.0

                    # 🖼️ رفع صور جديدة (اختياري)
                    uploaded_files = st.file_uploader(
                        "📷 ارفع صور جديدة (اختياري)",
                        type=["png", "jpg", "jpeg", "webp"],
                        accept_multiple_files=True,
                        key=f"upload_edit_{product['id']}"
                    )

                    existing_images = product.get("images", [])
                    if not isinstance(existing_images, list):
                        existing_images = []
                    if not existing_images and product.get("image"):
                        existing_images = [product["image"]]

                    if existing_images:
                        st.caption(f"الصور الحالية: {len(existing_images)}")
                        preview_cols = st.columns(min(len(existing_images), 4))
                        for i, img_url in enumerate(existing_images[:4]):
                            with preview_cols[i]:
                                st.image(img_url, use_container_width=True)

                    cc1, cc2 = st.columns(2)
                    if cc1.form_submit_button("💾 Save", use_container_width=True):
                        new_images = list(existing_images)
                        if uploaded_files:
                            for f in uploaded_files:
                                p = save_uploaded_image(f, product["id"])
                                if p:
                                    new_images.append(p)

                        update_product(CATEGORY_SLUG, product["id"], {
                            "id": product["id"],
                            "name": name,
                            "description": desc,
                            "price": price,
                            "price_after": price_after if has_disc else 0,
                            "images": new_images,
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

    images = p.get("images", [])
    if not isinstance(images, list):
        images = []
    if not images and p.get("image"):
        images = [p["image"]]

    if images:
        st.image(images[0], use_container_width=True)
        if len(images) > 1:
            extra_cols = st.columns(min(len(images) - 1, 4))
            for i, img in enumerate(images[1:]):
                with extra_cols[i % 4]:
                    st.image(img, use_container_width=True)

    st.write(p.get("description", ""))
    price = p.get("price", 0)
    price_after = p.get("price_after", 0)
    if price_after and price_after < price:
        st.markdown(f"~~{price:.0f} EGP~~ → **{price_after:.0f} EGP**")
    else:
        st.markdown(f"**{price:.0f} EGP**")

    st.link_button("💬 WhatsApp Us", get_whatsapp_link(p), use_container_width=True)

    if st.button("❌ Close"):
        st.session_state["view_product"] = None
        st.rerun()
