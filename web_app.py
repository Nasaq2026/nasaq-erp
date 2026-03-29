import streamlit as st
import os
import sys
import warnings
import psycopg2
from datetime import datetime

# --- 1. تهيئة المسارات ---
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

warnings.simplefilter('ignore', UserWarning)

st.set_page_config(page_title="نَسق ERP | الإدارة", page_icon="🎯", layout="wide")

# --- 2. الستايل ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] { direction: rtl; text-align: right; font-family: 'Cairo', sans-serif !important; }
    header, footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 3. إدارة الاتصال الذكي ---
@st.cache_resource(ttl=60)
def init_connection():
    try:
        # تأكد من أن هذا الرابط هو الصحيح لمشروعك الحالي
        db_uri = "postgresql://postgres.watkvwpzsxzdndhpmxsg:Nasaq268609@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres?prepareThreshold=0"
        return psycopg2.connect(db_uri, sslmode="require", connect_timeout=10)
    except Exception:
        return None

conn = init_connection()

# --- 4. محرك استدعاء الصفحات ---
def load_system_modules():
    pages = {}
    modules_map = {
        "dashboard": ("web_ui.dashboard", "render_dashboard"),
        "ai_assistant": ("web_ui.ai_assistant", "render_ai_assistant"),
        "new_order": ("web_ui.new_order", "render_new_order"),
        "orders": ("web_ui.orders", "render_orders"),
        "designer": ("web_ui.designer", "render_designer"),
        "installer": ("web_ui.installer", "render_installer")
    }
    for key, (path, func_name) in modules_map.items():
        try:
            module = __import__(path, fromlist=[func_name])
            pages[key] = getattr(module, func_name)
        except:
            pages[key] = lambda *args, **kwargs: st.error(f"⚠️ الموديول {key} غير مكتمل أو به خطأ في الكود")
    return pages

PAGES = load_system_modules()

if "logged_in" not in st.session_state:
    st.session_state.update({"logged_in": False, "emp_name": "", "role": ""})

# --- 5. منطق الواجهات ---
if not st.session_state.logged_in:
    st.title("🔐 تسجيل دخول نَسق")
    with st.form("login"):
        serial = st.text_input("الرقم الوظيفي")
        pwd = st.text_input("كلمة المرور", type="password")
        if st.form_submit_button("دخول"):
            if conn:
                cur = conn.cursor()
                cur.execute("SELECT emp_name, role FROM employees WHERE serial_number=%s AND password=%s", (serial, pwd))
                user = cur.fetchone()
                if user:
                    st.session_state.update({"logged_in": True, "emp_name": user[0], "role": user[1]})
                    st.rerun()
                else: st.error("بيانات الدخول غير صحيحة")
            else: st.error("🔴 السيرفر غير متصل حالياً، حاول لاحقاً")
else:
    with st.sidebar:
        st.markdown(f"### 🎯 نَسق | {st.session_state.emp_name}")
        st.info("🟢 متصل" if conn else "🔴 منقطع")
        
        if st.session_state.role == "Admin":
            menu = ["📊 لوحة القيادة", "🤖 المساعد الذكي", "➕ طلب جديد", "📦 الورشة"]
        else:
            menu = ["🏠 شاشتي الرئيسية", "🤖 المساعد الذكي"]
        
        choice = st.radio("القائمة", menu)
        if st.button("🚪 خروج"):
            st.session_state.logged_in = False
            st.rerun()

    # تحويل الاختيار لمفتاح موديول
    nav_map = {
        "📊 لوحة القيادة": "dashboard", "🤖 المساعد الذكي": "ai_assistant", 
        "➕ طلب جديد": "new_order", "📦 الورشة": "orders", "🏠 شاشتي الرئيسية": "my_screen"
    }
    selected_key = nav_map.get(choice)

    # التشغيل الآمن للموديولات
    if selected_key == "my_screen":
        role_map = {"Designer": "designer", "Installer": "installer"}
        key = role_map.get(st.session_state.role)
        if key in PAGES: PAGES[key](conn, st.session_state.emp_name)
    elif selected_key in PAGES:
        # تمرير conn لكل الموديولات
        PAGES[selected_key](conn)
