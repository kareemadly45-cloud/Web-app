import json
import base64
import streamlit as st
from pathlib import Path

# ============================================
# Paths
# ============================================
DATA_DIR = Path("data")
DATA_FILE = DATA_DIR / "products.json"
UPLOADS_DIR = Path("uploads")

# ============================================
# Categories
# ============================================
CATEGORIES = {
    "home": {
        "name": "Home",
        "icon": "🏠",
        "page": "1_Home",
        "color": "#FF6B6B",
        "image": "https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=300&h=300&fit=crop",
    },
    "luxury": {
        "name": "Luxury",
        "icon": "💎",
        "page": "2_Luxury",
        "color": "#9B59B6",
        "image": "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=300&h=300&fit=crop",
    },
    "soree": {
        "name": "Soree",
        "icon": "🛍️",
        "page": "3_Soree",
        "color": "#3498DB",
        "image": "https://images.unsplash.com/photo-1566150905458-1bf1fc113f0d?w=300&h=300&fit=crop",
    },
    "discount": {
        "name": "Discount",
        "icon": "🔥",
        "page": "4_Discount",
        "color": "#E74C3C",
        "image": "https://images.unsplash.com/photo-1607083206968-13611e3d76db?w=300&h=300&fit=crop",
    }


# ============================================
# Admin
# ============================================
def get_admin_password():
    try:
        return st.secrets["ADMIN_PASSWORD"]
    except (KeyError, FileNotFoundError):
        return "admin123"


def is_admin():
    return st.session_state.get("is_admin", False)


def login_admin(password):
    if password == get_admin_password():
        st.session_state.is_admin = True
        return True
    return False


def logout_admin():
    st.session_state.is_admin = False


# ============================================
# Database
# ============================================
def init_db():
    DATA_DIR.mkdir(exist_ok=True)
    if not DATA_FILE.exists():
        default_data = {cat: [] for cat in CATEGORIES.keys()}
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(default_data, f, ensure_ascii=False, indent=2)


def load_products():
    init_db()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_products(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_products(category):
    return load_products().get(category, [])


def add_product(category, product):
    data = load_products()
    data.setdefault(category, []).append(product)
    save_products(data)


def update_product(category, product_id, updated):
    data = load_products()
    for i, p in enumerate(data.get(category, [])):
        if p["id"] == product_id:
            data[category][i] = updated
            break
    save_products(data)


def delete_product(category, product_id):
    data = load_products()
    data[category] = [p for p in data.get(category, []) if p["id"] != product_id]
    save_products(data)


# ============================================
# Image Handling
# ============================================
def save_uploaded_image(uploaded_file, product_id):
    """حفظ الصورة المرفوعة في مجلد uploads"""
    if uploaded_file is None:
        return ""
    UPLOADS_DIR.mkdir(exist_ok=True)
    ext = uploaded_file.name.split(".")[-1].lower()
    import uuid
    filename = f"{product_id}_{uuid.uuid4().hex[:8]}.{ext}"
    filepath = UPLOADS_DIR / filename
    with open(filepath, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return str(filepath)


def image_to_base64(path):
    """تحويل الصورة لـ Base64 عشان تظهر في HTML"""
    try:
        with open(path, "rb") as f:
            data = f.read()
        ext = path.split(".")[-1].lower()
        if ext == "jpg":
            ext = "jpeg"
        return f"data:image/{ext};base64,{base64.b64encode(data).decode()}"
    except Exception:
        return ""


# ============================================
# CSS Helpers
# ============================================
def hide_streamlit_ui():
    """إخفاء عناصر Streamlit الافتراضية"""
    st.markdown("""
<style>
    header[data-testid="stHeader"] { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    [data-testid="stToolbarActions"] { display: none !important; }
    .stDeployButton { display: none !important; }
    .stAppDeployButton { display: none !important; }
    [data-testid="stAppDeployButton"] { display: none !important; }
    [data-testid="stStatusWidget"] { display: none !important; }
    #MainMenu { visibility: hidden !important; }
    footer { visibility: hidden !important; }
    [data-testid="stDecoration"] { display: none !important; }
    [data-testid="manage-app-button"] { display: none !important; }
    .viewerBadge_container__1QSob { display: none !important; }
    .viewerBadge_link__1S137 { display: none !important; }
    .viewerBadge_text__1JaDK { display: none !important; }
</style>
""", unsafe_allow_html=True)


# ============================================
# Product Card
# ============================================
def calc_discount(price_before, price_after):
    if price_before and price_after and price_before > price_after:
        return int(((price_before - price_after) / price_before) * 100)
    return 0


def render_product_card(product):
    price = product.get("price", 0)
    price_after = product.get("price_after", 0)
    has_discount = price_after and price_after < price
    discount = calc_discount(price, price_after) if has_discount else 0

    images = product.get("images", [])
    if not images and product.get("image"):
        images = [product["image"]]

    img_src = ""
    if images:
        first = images[0]
        img_src = first if first.startswith("http") else image_to_base64(first)

    if img_src:
        img_html = f'<img src="{img_src}" style="width:100%;height:220px;object-fit:cover;border-radius:10px;">'
    else:
        img_html = '<div style="width:100%;height:220px;background:#2a2a2a;border-radius:10px;display:flex;align-items:center;justify-content:center;color:#999;">No Image</div>'

    badge = ""
    if has_discount:
        badge = f'<span style="background:#e74c3c;color:white;padding:3px 10px;border-radius:20px;font-size:12px;font-weight:bold;">-{discount}%</span>'

    if has_discount:
        price_html = f'<span style="text-decoration:line-through;color:#999;font-size:14px;">{price:.0f} EGP</span> <span style="color:#e74c3c;font-weight:bold;font-size:18px;">{price_after:.0f} EGP</span>'
    else:
        price_html = f'<span style="font-weight:bold;font-size:18px;">{price:.0f} EGP</span>'

    html = (
        f'<div style="border:1px solid #333;border-radius:12px;padding:12px;background:#1a1a1a;">'
        f'{img_html}'
        f'<div style="display:flex;justify-content:space-between;align-items:center;margin-top:10px;">'
        f'<div style="font-weight:600;font-size:16px;">{product["name"]}</div>'
        f'{badge}'
        f'</div>'
        f'<div style="margin-top:8px;">{price_html}</div>'
        f'<div style="color:#999;font-size:13px;margin-top:5px;">{product.get("description","")}</div>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


# ============================================
# WhatsApp
# ============================================
def whatsapp_link(product_name=""):
    import urllib.parse
    try:
        number = st.secrets["WHATSAPP_NUMBER"]
        msg = st.secrets["WHATSAPP_MESSAGE"]
    except (KeyError, FileNotFoundError):
        number = "201012345678"
        msg = "مرحبا، عايز أستفسر عن منتجات La Mariposa"
    if product_name:
        msg = f"{msg}\n\nالمنتج: {product_name}"
    return f"https://wa.me/{number}?text={urllib.parse.quote(msg)}"
