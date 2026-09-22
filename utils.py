import json
import uuid
import base64
import requests
import streamlit as st
from pathlib import Path


DATA_DIR = Path("data")
DATA_FILE = DATA_DIR / "products.json"
ASSETS_DIR = Path("assets")

try:
    GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
    GITHUB_REPO = st.secrets["GITHUB_REPO"]
    GITHUB_BRANCH = st.secrets.get("GITHUB_BRANCH", "main")
except Exception:
    GITHUB_TOKEN = ""
    GITHUB_REPO = ""
    GITHUB_BRANCH = "main"

GITHUB_FILE_PATH = "data/products.json"
GITHUB_API_URL = "https://api.github.com"

WHATSAPP_NUMBER = "201012345688"
WHATSAPP_MESSAGE = "مرحبا، عايز أستفسر عن منتجات La Mariposa Store"

try:
    ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]
except Exception:
    ADMIN_PASSWORD = "admin123"

CATEGORIES = {
    "home": {"name": "Home", "icon": "🏠", "page": "1_Home", "color": "#FF6B6B",
             "image": "https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=300&h=300&fit=crop"},
    "luxury": {"name": "Luxury", "icon": "💎", "page": "2_Luxury", "color": "#9B59B6",
               "image": "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=300&h=300&fit=crop"},
    "soree": {"name": "Soree", "icon": "🛍️", "page": "3_Soree", "color": "#3498DB",
              "image": "https://images.unsplash.com/photo-1566150905458-1bf1fc113f0d?w=300&h=300&fit=crop"},
    "discount": {"name": "Discount", "icon": "🔥", "page": "4_Discount", "color": "#E74C3C",
                 "image": "https://images.unsplash.com/photo-1607083206968-13611e3d76db?w=300&h=300&fit=crop"},
}


def github_enabled():
    return bool(GITHUB_TOKEN and GITHUB_REPO)


def github_headers():
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def get_github_file():
    """بدون أي st.error"""
    if not github_enabled():
        return None, None
    try:
        api_url = f"{GITHUB_API_URL}/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
        r = requests.get(api_url, headers=github_headers(), params={"ref": GITHUB_BRANCH}, timeout=15)
        if r.status_code != 200:
            return None, None
        meta = r.json()
        sha = meta.get("sha")
        content = meta.get("content", "")
        download_url = meta.get("download_url")
        decoded = ""
        if content:
            try:
                decoded = base64.b64decode(content.replace("\n", "")).decode("utf-8").strip()
            except Exception:
                decoded = ""
        elif download_url:
            try:
                raw = requests.get(download_url, timeout=30)
                if raw.status_code == 200:
                    decoded = raw.text.strip()
            except Exception:
                decoded = ""
        if not decoded:
            return None, sha
        try:
            return json.loads(decoded), sha
        except Exception:
            return None, sha
    except Exception:
        return None, None


def save_to_github(data, sha=None):
    """بدون أي st.error"""
    if not github_enabled():
        return False
    try:
        url = f"{GITHUB_API_URL}/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
        json_content = json.dumps(data, ensure_ascii=False, indent=2)
        encoded = base64.b64encode(json_content.encode("utf-8")).decode("utf-8")
        payload = {"message": "Update products", "content": encoded, "branch": GITHUB_BRANCH}
        if sha:
            payload["sha"] = sha
        r = requests.put(url, headers=github_headers(), json=payload, timeout=30)
        return r.status_code in [200, 201]
    except Exception:
        return False


def init_db():
    DATA_DIR.mkdir(exist_ok=True)
    ASSETS_DIR.mkdir(exist_ok=True)
    if not DATA_FILE.exists():
        default_data = {cat: [] for cat in CATEGORIES.keys()}
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(default_data, f, ensure_ascii=False, indent=2)


def load_products():
    init_db()
    if github_enabled():
        github_data, _ = get_github_file()
        if github_data is not None:
            try:
                with open(DATA_FILE, "w", encoding="utf-8") as f:
                    json.dump(github_data, f, ensure_ascii=False, indent=2)
            except Exception:
                pass
            return github_data
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {cat: [] for cat in CATEGORIES.keys()}


def save_products(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
    if github_enabled():
        _, sha = get_github_file()
        return save_to_github(data, sha=sha)
    return True


def get_products(category):
    return load_products().get(category, [])


def add_product(category, product):
    data = load_products()
    data.setdefault(category, []).append(product)
    return save_products(data)


def update_product(category, product_id, updated):
    data = load_products()
    for i, p in enumerate(data.get(category, [])):
        if p["id"] == product_id:
            data[category][i] = updated
            break
    return save_products(data)


def delete_product(category, product_id):
    data = load_products()
    data[category] = [p for p in data.get(category, []) if p["id"] != product_id]
    return save_products(data)


def save_uploaded_image(uploaded_file, product_id=None):
    if uploaded_file is None:
        return ""
    try:
        data = uploaded_file.getvalue()
        ext = uploaded_file.name.split(".")[-1].lower() if "." in uploaded_file.name else "png"
        if len(data) > 100 * 1024:
            try:
                from PIL import Image
                import io
                img = Image.open(io.BytesIO(data))
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                if img.width > 700 or img.height > 700:
                    img.thumbnail((700, 700), Image.LANCZOS)
                output = io.BytesIO()
                img.save(output, "JPEG", quality=65, optimize=True)
                data = output.getvalue()
                ext = "jpeg"
            except Exception:
                if ext == "jpg":
                    ext = "jpeg"
        else:
            if ext == "jpg":
                ext = "jpeg"
        return f"data:image/{ext};base64,{base64.b64encode(data).decode()}"
    except Exception:
        return ""


def get_product_images(product):
    images = product.get("images", [])
    if not isinstance(images, list):
        images = []
    if not images and product.get("image"):
        images = [product["image"]]
    return images


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


def is_admin():
    return st.session_state.get("is_admin", False)


def login_admin(password):
    if password == ADMIN_PASSWORD:
        st.session_state.is_admin = True
        return True
    return False


def logout_admin():
    st.session_state.is_admin = False


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
    msg_encoded = msg.replace(" ", "%20").replace("\n", "%0A")
    return f"https://wa.me/{WHATSAPP_NUMBER}?text={msg_encoded}"


def hide_streamlit_ui():
    st.markdown("""
<style>
    /* ============================================
       إخفاء عناصر Streamlit الافتراضية
       ============================================ */
    header[data-testid="stHeader"] { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    [data-testid="stToolbarActions"] { display: none !important; }
    .stDeployButton { display: none !important; }
    [data-testid="stAppDeployButton"] { display: none !important; }
    [data-testid="stStatusWidget"] { display: none !important; }
    #MainMenu { visibility: hidden !important; }
    footer { visibility: hidden !important; }
    [data-testid="stDecoration"] { display: none !important; }
    [data-testid="manage-app-button"] { display: none !important; }

    /* ============================================
       إخفاء رسائل الأخطاء
       ============================================ */
    div[data-testid="stAlert"],
    div[data-baseweb="notification"],
    div.stAlert,
    .stException,
    div[data-testid="stException"],
    div[role="alert"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

def render_product_card(product):
    price = product.get("price", 0)
    price_after = product.get("price_after", 0)
    has_discount = price_after and price_after < price
    discount = calc_discount(price, price_after) if has_discount else 0
    images = get_product_images(product)
    img_src = images[0] if images else ""
    if img_src:
        img_html = '<img src="' + img_src + '" style="width:100%;height:240px;object-fit:cover;border-radius:12px;">'
    else:
        img_html = '<div style="width:100%;height:240px;background:#2a2a2a;border-radius:12px;display:flex;align-items:center;justify-content:center;color:#666;">No Image</div>'
    badge = ""
    if has_discount:
        badge = '<span style="background:linear-gradient(135deg,#800020,#B22234);color:white;padding:5px 14px;border-radius:20px;font-size:13px;font-weight:bold;">-' + str(discount) + '%</span>'
    if has_discount:
        price_html = '<span style="text-decoration:line-through;color:#666;font-size:15px;">' + str(int(price)) + ' EGP</span> <span style="color:#800020;font-weight:bold;font-size:22px;margin-left:8px;">' + str(int(price_after)) + ' EGP</span>'
    else:
        price_html = '<span style="color:#F39C12;font-weight:bold;font-size:22px;">' + str(int(price)) + ' EGP</span>'
    name = product.get("name", "")
    desc = product.get("description", "")
    html = (
        '<div style="border:2px solid #800020;border-radius:15px;padding:14px;background:#1a1a1a;margin-bottom:10px;box-shadow:0 4px 15px rgba(128,0,32,0.3);">'
        + img_html +
        '<div style="display:flex;justify-content:space-between;align-items:center;margin-top:12px;">'
        '<div style="font-weight:700;font-size:17px;color:#ffffff;">' + name + '</div>'
        + badge + '</div>'
        '<div style="margin-top:10px;">' + price_html + '</div>'
        '<div style="color:#999;font-size:14px;margin-top:6px;">' + desc + '</div>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)

st.error(f"GitHub read error: {e}")
st.error(f"GitHub save error: {error_message}")
st.error(f"GitHub connection error: {e}")
st.error(f"Error processing image: {e}")
