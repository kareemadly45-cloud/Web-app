import json
import base64
import uuid
import urllib.parse
import streamlit as st
from pathlib import Path

# ============================================
# Paths
# ============================================
DATA_DIR = Path("data")
DATA_FILE = DATA_DIR / "products.json"
ASSETS_DIR = Path("assets")
UPLOADS_DIR = Path("uploads")

# ============================================
# 📱 WhatsApp Settings
# ============================================
WHATSAPP_NUMBER = "201012345678"
WHATSAPP_MESSAGE = "مرحبا، عايز أستفسر عن منتجات La Mariposa Store"

# ============================================
# 🔐 Admin Password
# ============================================
try:
    ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]
except Exception:
    ADMIN_PASSWORD = "admin123"


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
    },
}


# ============================================
# Database
# ============================================
def init_db():
    DATA_DIR.mkdir(exist_ok=True)
    ASSETS_DIR.mkdir(exist_ok=True)
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
# 📸 Image Handling
# ============================================
def save_uploaded_image(uploaded_file, product_id=None):
    """حفظ الصورة في assets/ وإرجاع مسارها"""
    if uploaded_file is None:
        return ""

    ASSETS_DIR.mkdir(exist_ok=True)

    original_name = uploaded_file.name
    ext = original_name.split(".")[-1].lower() if "." in original_name else "png"

    if product_id is None:
        product_id = str(uuid.uuid4())

    # اسم فريد لكل صورة عشان لو فيه أكتر من صورة لنفس المنتج
    filename = f"{product_id}_{uuid.uuid4().hex[:6]}.{ext}"
    filepath = ASSETS_DIR / filename

    with open(filepath, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return str(filepath).replace("\\", "/")


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


def resolve_image_src(path):
    """يرجع src مناسب: لو رابط → يرجع زي ما هو، لو ملف محلي → Base64"""
    if not path:
        return ""
    if path.startswith("http://") or path.startswith("https://"):
        return path
    return image_to_base64(path)


# ============================================
# 🛒 Cart
# ============================================
def init_cart():
    if "cart" not in st.session_state:
        st.session_state.cart = []


def add_to_cart(product, category):
    init_cart()
    st.session_state.cart.append({**product, "category": category})


def remove_from_cart(index):
    init_cart()
    if 0 <= index < len(st.session_state.cart):
        st.session_state.cart.pop(index)


def get_cart_count():
    init_cart()
    return len(st.session_state.cart)


def get_cart_items():
    init_cart()
    return st.session_state.cart


def get_cart_total():
    init_cart()
    total = 0
    for item in st.session_state.cart:
        price = item.get("price_after") or item.get("price", 0)
        total += price
    return total


def clear_cart():
    st.session_state.cart = []


# ============================================
# Admin Session
# ============================================
def is_admin():
    return st.session_state.get("is_admin", False)


def login_admin(password):
    if password == ADMIN_PASSWORD:
        st.session_state.is_admin = True
        return True
    return False


def logout_admin():
    st.session_state.is_admin = False


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
</style>
""", unsafe_allow_html=True)


# ============================================
# Helpers
# ============================================
def calc_discount(price_before, price_after):
    if price_before and price_after and price_before > price_after:
        return int(((price_before - price_after) / price_before) * 100)
    return 0


def get_whatsapp_link(product=None):
    msg = WHATSAPP_MESSAGE
    if product:
        msg = f"مرحبا، عايز أستفسر عن: {product['name']}"
        price = product.get("price", 0)
        price_after = product.get("price_after", 0)
        if price_after and price_after < price:
            msg += f" (السعر: {price_after:.0f} EGP بدل {price:.0f} EGP)"
        else:
            msg += f" (السعر: {price:.0f} EGP)"

    # urllib أفضل من replace للحروف العربية
    encoded = urllib.parse.quote(msg)
    return f"https://wa.me/{WHATSAPP_NUMBER}?text={encoded}"


# ============================================
# Product Card (بدون indentation في HTML)
# ============================================
def render_product_card(product):
    price = product.get("price", 0)
    price_after = product.get("price_after", 0)
    has_discount = price_after and price_after < price
    discount = calc_discount(price, price_after) if has_discount else 0

    # دعم الصور المتعددة
    images = product.get("images", [])
    if not images and product.get("image"):
        images = [product["image"]]

    img_src = ""
    if images:
        img_src = resolve_image_src(images[0])

    if img_src:
        img_html = f'<img src="{img_src}" style="width:100%;height:240px;object-fit:cover;border-radius:12px;">'
    else:
        img_html = '<div style="width:100%;height:240px;background:#2a2a2a;border-radius:12px;display:flex;align-items:center;justify-content:center;color:#666;">No Image</div>'

    badge = ""
    if has_discount:
        badge = f'<span style="background:linear-gradient(135deg,#800020,#B22234);color:white;padding:5px 14px;border-radius:20px;font-size:13px;font-weight:bold;">-{discount}%</span>'

    if has_discount:
        price_html = f'<span style="text-decoration:line-through;color:#666;font-size:15px;">{price:.0f} EGP</span> <span style="color:#800020;font-weight:bold;font-size:22px;margin-left:8px;">{price_after:.0f} EGP</span>'
    else:
        price_html = f'<span style="color:#F39C12;font-weight:bold;font-size:22px;">{price:.0f} EGP</span>'

    # ⚠️ HTML من غير أي indentation نهائياً
    html = (
        '<div style="border:2px solid #800020;border-radius:15px;padding:14px;background:#1a1a1a;margin-bottom:10px;box-shadow:0 4px 15px rgba(128,0,32,0.3);">'
        f'{img_html}'
        '<div style="display:flex;justify-content:space-between;align-items:center;margin-top:12px;">'
        f'<div style="font-weight:700;font-size:17px;color:#ffffff;">{product["name"]}</div>'
        f'{badge}'
        '</div>'
        f'<div style="margin-top:10px;">{price_html}</div>'
        f'<div style="color:#999;font-size:14px;margin-top:6px;">{product.get("description", "")}</div>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)
