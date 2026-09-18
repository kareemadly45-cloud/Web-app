import uuid
import streamlit as st
from pathlib import Path

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError as e:
    create_client = None
    Client = None
    SUPABASE_AVAILABLE = False
    SUPABASE_IMPORT_ERROR = str(e)

# ============================================
# Paths
# ============================================
DATA_DIR = Path("data")
ASSETS_DIR = Path("assets")
BUCKET_NAME = "product-images"

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
# 🗄️ Supabase Client
# ============================================
@st.cache_resource
def get_supabase():
    # الرابط مكتوب بالكامل بحروف إنجليزية (Latin)
    url = "https://scpaqujqzckxuuyibsze.supabase.co"
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)
# ============================================
# Categories
# ============================================
CATEGORIES = {
    "home": {
        "name": "Home", "icon": "🏠", "page": "1_Home", "color": "#FF6B6B",
        "image": "https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=300&h=300&fit=crop",
    },
    "luxury": {
        "name": "Luxury", "icon": "💎", "page": "2_Luxury", "color": "#9B59B6",
        "image": "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=300&h=300&fit=crop",
    },
    "soree": {
        "name": "Soree", "icon": "🛍️", "page": "3_Soree", "color": "#3498DB",
        "image": "https://images.unsplash.com/photo-1566150905458-1bf1fc113f0d?w=300&h=300&fit=crop",
    },
    "discount": {
        "name": "Discount", "icon": "🔥", "page": "4_Discount", "color": "#E74C3C",
        "image": "https://images.unsplash.com/photo-1607083206968-13611e3d76db?w=300&h=300&fit=crop",
    },
}


# ============================================
# Database (Supabase)
# ============================================
def init_db():
    """مش محتاجة مع Supabase"""
    DATA_DIR.mkdir(exist_ok=True)
    ASSETS_DIR.mkdir(exist_ok=True)


def get_products(category):
    """جلب منتجات كاتيجوري من Supabase"""
    try:
        supabase = get_supabase()
        response = (
            supabase.table("products")
            .select("*")
            .eq("category", category)
            .order("created_at", desc=True)
            .execute()
        )
        products = response.data or []
        for p in products:
            if not isinstance(p.get("images"), list):
                p["images"] = []
        return products
    except Exception as e:
        st.error(f"Error loading products: {e}")
        return []


def add_product(category, product):
    """إضافة منتج في Supabase"""
    try:
        supabase = get_supabase()
        data = {
            "category": category,
            "name": product["name"],
            "description": product.get("description", ""),
            "price": float(product.get("price", 0)),
            "price_after": float(product.get("price_after", 0)),
            "images": product.get("images", []),
        }
        response = supabase.table("products").insert(data).execute()
        return response.data
    except Exception as e:
        st.error(f"Error adding product: {e}")
        return None


def update_product(category, product_id, updated):
    """تعديل منتج"""
    try:
        supabase = get_supabase()
        data = {
            "name": updated["name"],
            "description": updated.get("description", ""),
            "price": float(updated.get("price", 0)),
            "price_after": float(updated.get("price_after", 0)),
            "images": updated.get("images", []),
        }
        supabase.table("products").update(data).eq("id", product_id).execute()
        return True
    except Exception as e:
        st.error(f"Error updating product: {e}")
        return False


def delete_product(category, product_id):
    """حذف منتج + صوره من Storage"""
    try:
        supabase = get_supabase()

        # امسح الصور من Storage
        product = supabase.table("products").select("images").eq("id", product_id).execute()
        if product.data:
            images = product.data[0].get("images", [])
            for img_url in images:
                try:
                    filename = img_url.split("/")[-1]
                    supabase.storage.from_(BUCKET_NAME).remove([filename])
                except Exception:
                    pass

        # امسح المنتج
        supabase.table("products").delete().eq("id", product_id).execute()
        return True
    except Exception as e:
        st.error(f"Error deleting product: {e}")
        return False


# ============================================
# 📸 Image Upload (Supabase Storage)
# ============================================
def save_uploaded_image(uploaded_file, product_id=None):
    """حفظ الصورة في Supabase Storage وإرجاع الرابط"""
    if uploaded_file is None:
        return ""

    try:
        supabase = get_supabase()

        if product_id is None:
            product_id = str(uuid.uuid4())

        original_name = uploaded_file.name
        ext = original_name.split(".")[-1].lower() if "." in original_name else "png"
        filename = f"{product_id}_{uuid.uuid4().hex[:8]}.{ext}"

        # ارفع الصورة
        supabase.storage.from_(BUCKET_NAME).upload(
            path=filename,
            file=uploaded_file.getvalue(),
            file_options={"content-type": uploaded_file.type or f"image/{ext}"},
        )

        # ارجع الرابط العام
        public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(filename)
        return public_url

    except Exception as e:
        st.error(f"Error uploading image: {e}")
        return ""


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

    msg_encoded = msg.replace(" ", "%20").replace("\n", "%0A")
    return f"https://wa.me/{WHATSAPP_NUMBER}?text={msg_encoded}"


def hide_streamlit_ui():
    """إخفاء عناصر Streamlit"""
    st.markdown("""
<style>
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
</style>
""", unsafe_allow_html=True)


def render_product_card(product):
    price = product.get("price", 0)
    price_after = product.get("price_after", 0)
    has_discount = price_after and price_after < price
    discount = calc_discount(price, price_after) if has_discount else 0

    # دعم الصور المتعددة — نعرض أول صورة
    images = product.get("images", [])
    if not isinstance(images, list):
        images = []
    img_src = images[0] if images else ""

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

    st.markdown(f"""
    <div style="border:2px solid #800020;border-radius:15px;padding:14px;background:#1a1a1a;margin-bottom:10px;box-shadow:0 4px 15px rgba(128,0,32,0.3);">
        {img_html}
        <div style="display:flex;justify-content:space-between;align-items:center;margin-top:12px;">
            <div style="font-weight:700;font-size:17px;color:#ffffff;">{product['name']}</div>
            {badge}
        </div>
        <div style="margin-top:10px;">{price_html}</div>
        <div style="color:#999;font-size:14px;margin-top:6px;">{product.get('description', '')}</div>
    </div>
    """, unsafe_allow_html=True)
