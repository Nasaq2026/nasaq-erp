import streamlit as st
import os
import sys
import warnings
import psycopg2
from datetime import datetime

# --- 1. تهيئة المسارات وبيئة العمل ---
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

warnings.simplefilter('ignore', UserWarning)

st.set_page_config(
    page_title="نَسق ERP | الإدارة الذكية", 
    page_icon="🎯", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. ستايل نَسق (Master CSS) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {
    direction: rtl; text-align: right; font-family: 'Cairo', sans-serif !important;
}
[data-testid="stSidebar"] { background-color: #0b1329 !important; }
header, footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 3. إدارة الاتصال (تم تحديث الرابط والباسورد) ---
@st.cache_resource(ttl=60)
@st.cache_resource(ttl=60)
def init_connection():
    try:
        # لاحظ إضافة ?prepareThreshold=0 في النهاية
        db_uri = "postgresql://postgres.watkvwpzsxzdndhpmxsg:Nasaq268609@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres?prepareThreshold=0"
        return psycopg2.connect(db_uri, sslmode="require", connect_timeout=15)
    except Exception as e:
        return None

conn = init_connection()

# --- 4. محرك استدعاء الصفحات التلقائي ---
def load_system_modules():
    pages = {}
    modules_map = {
        "dashboard": ("web_ui.dashboard", "render_dashboard"),
        "ai_assistant": ("web_ui.ai_assistant", "render_ai_assistant"),
        "new_order": ("web_ui.new_order", "render_new_order"),
        "orders": ("web_ui.orders", "render_orders"),
        "designer": ("web_ui.designer", "render_designer"),
        "tech": ("web_ui.technician", "render_technician"),
        "installer": ("web_ui.installer", "render_installer")
    }
    
    for key, (path, func_name) in modules_map.items():
        try:
            module = __import__(path, fromlist=[func_name])
            pages[key] = getattr(module, func_name)
        except Exception:
            pages[key] = None # نضعها None إذا فشل التحميل
            
    return pages

PAGES = load_system_modules()

if "logged_in" not in st.session_state:
    st.session_state.update({"logged_in": False, "emp_name": "", "role": ""})

# --- 5. واجهة تسجيل الدخول ---
def show_login_screen():
    st.write("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.3, 1])
    with c2:
        st.markdown("<h1 style='text-align:center; color:#38bdf8;'>نَسق للخدمات الإعلانية</h1>", unsafe_allow_html=True)
        if not conn:
            st.error("🔴 خطأ في الاتصال بالسيرفر. تأكد من إعدادات Supabase والـ IP.")
        
        with st.form("login_form"):
            serial = st.text_input("الرقم الوظيفي")
            pwd = st.text_input("كلمة المرور", type="password")
            if st.form_submit_button("دخول للنظام 🚀", use_container_width=True):
                if conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT emp_name, role FROM employees WHERE serial_number = %s AND password = %s", (serial, pwd))
                    user = cursor.fetchone()
                    if user:
                        st.session_state.update({"logged_in": True, "emp_name": user[0], "role": user[1]})
                        st.rerun()
                    else: st.error("بيانات الدخول غير صحيحة")
                else: st.error("لا يمكن تسجيل الدخول بدون اتصال بالسيرفر")

# --- 6. البوابة الرئيسية ---
def show_main_portal():
    with st.sidebar:
        st.markdown("### 🎯 نَسق ERP")
        if conn:
            st.success(f"🟢 متصل: {st.session_state.emp_name}")
        else:
            st.error("🔴 السيرفر منقطع")
        
        st.divider()
        if st.session_state.role == "Admin":
            menu = ["📊 لوحة القيادة", "🤖 المساعد الذكي", "➕ طلب جديد", "📦 الورشة"]
        else:
            menu = ["🏠 شاشتي الرئيسية", "🤖 المساعد الذكي"]
            
        choice = st.radio("القائمة", menu, label_visibility="collapsed")
        if st.button("🚪 خروج", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    nav_map = {
        "📊 لوحة القيادة": "dashboard", "🤖 المساعد الذكي": "ai_assistant", 
        "➕ طلب جديد": "new_order", "📦 الورشة": "orders", "🏠 شاشتي الرئيسية": "my_screen"
    }
    
    selected_key = nav_map.get(choice)
    
    # حماية: إذا كان الاتصال مقطوعاً لا تحاول تشغيل الموديول
    if not conn and selected_key != "ai_assistant":
        st.warning("⚠️ يرجى الانتظار حتى عودة الاتصال بالسيرفر..")
        return

    if selected_key == "my_screen":
        role = st.session_state.role
        role_map = {"Designer": "designer", "Technician": "tech", "Installer": "installer"}
        key = role_map.get(role)
        if key in PAGES and PAGES[key]: PAGES[key](conn, st.session_state.emp_name)
    elif selected_key in PAGES and PAGES[selected_key]:
        # نرسل الـ conn فقط إذا كان الموديول جاهزاً
        try:
            PAGES[selected_key](conn)
        except TypeError: # لبعض الموديولات التي لا تقبل conn
            PAGES[selected_key]()
    else:
        st.error(f"⚠️ الموديول {choice} غير متوفر حالياً")

# --- 7. التشغيل ---
if not st.session_state.logged_in:
    show_login_screen()
else:
    show_main_portal()
