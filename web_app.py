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

# --- 2. ستايل نَسق الاحترافي المطور (Master CSS) ---
NASQ_UI_THEME = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');
html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {
    direction: rtl;
    text-align: right;
    font-family: 'Cairo', sans-serif !important;
}
[data-testid="stSidebar"] {
    background-color: #0b1329 !important;
    border-left: 1px solid #1e293b;
}
div[data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] label {
    color: #e2e8f0 !important;
    background-color: rgba(255, 255, 255, 0.03) !important;
    padding: 14px 18px !important;
    border-radius: 12px !important;
    width: 100% !important;
    display: flex !important;
    margin-bottom: 8px !important;
}
div[data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] label:hover {
    background-color: rgba(56, 189, 248, 0.1) !important;
}
header {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(NASQ_UI_THEME, unsafe_allow_html=True)

# --- 3. إدارة الاتصال بقاعدة البيانات (تم تحديث الرابط للبروجكت الجديد) ---
@st.cache_resource(ttl=60)
def init_connection():
    try:
        # ✅ تم تحديث الـ ID ليكون watkvwpzsxzdndhpmxsg
        db_uri = "postgresql://postgres.watkvwpzsxzdndhpmxsg:Nasaq268609@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"
        return psycopg2.connect(db_uri, sslmode="require", connect_timeout=15)
    except Exception as e:
        st.sidebar.error(f"خطأ اتصال: {e}")
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
        "accounts": ("web_ui.accounts", "render_accounts"),
        "marketing": ("web_ui.marketing", "render_marketing"),
        "whatsapp": ("web_ui.whatsapp_sender", "render_whatsapp_sender"),
        "clients": ("web_ui.clients", "render_clients"),
        "employees": ("web_ui.employees", "render_employees"),
        "categories": ("web_ui.categories", "render_categories"),
        "designer": ("web_ui.designer", "render_designer"),
        "tech": ("web_ui.technician", "render_technician"),
        "installer": ("web_ui.installer", "render_installer")
    }
    
    for key, (path, func_name) in modules_map.items():
        try:
            module = __import__(path, fromlist=[func_name])
            pages[key] = getattr(module, func_name)
        except Exception as e:
            # دالة بديلة في حال فشل الاستدعاء لتوضيح الخطأ التقني
            pages[key] = lambda *args, **kwargs: st.error(f"⚠️ الموديول {key} يحتاج تحديث. الخطأ: {e}")
            
    return pages

PAGES = load_system_modules()

if "logged_in" not in st.session_state:
    st.session_state.update({"logged_in": False, "emp_name": "", "role": ""})

# --- 5. دالة التحية ---
def get_time_greeting():
    hour = datetime.now().hour
    if hour < 12: return "صباح الخير"
    elif hour < 18: return "مساء الخير"
    return "تمنياتنا بليلة سعيدة"

# --- 6. واجهة تسجيل الدخول ---
def show_login_screen():
    st.write("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.3, 1])
    with c2:
        st.markdown("<h1 style='text-align:center; color:#38bdf8;'>نَسق للخدمات الإعلانية</h1>", unsafe_allow_html=True)
        with st.form("login_form"):
            serial = st.text_input("الرقم الوظيفي (مثال: A-1001)")
            pwd = st.text_input("كلمة المرور", type="password")
            if st.form_submit_button("دخول للنظام 🚀", use_container_width=True):
                if conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT emp_name, role FROM employees WHERE serial_number = %s AND password = %s", (serial, pwd))
                    user = cursor.fetchone()
                    if user:
                        st.session_state.update({"logged_in": True, "emp_name": user[0], "role": user[1]})
                        st.rerun()
                    else:
                        st.error("بيانات الدخول غير صحيحة!")
                else:
                    st.error("فشل الاتصال بالقاعدة!")

# --- 7. البوابة الرئيسية (تعديل الـ Navigation) ---
def show_main_portal():
    greeting = get_time_greeting()
    
    with st.sidebar:
        st.markdown(f"### 🎯 نَسق ERP")
        status_text = "🟢 متصل" if conn else "🔴 منقطع"
        st.markdown(f"<div style='text-align:center; padding:10px; background:rgba(255,255,255,0.05); border-radius:10px;'>{greeting}، {st.session_state.emp_name}<br><b style='color:#38bdf8;'>{status_text}</b></div>", unsafe_allow_html=True)
        st.divider()
        
        # القائمة بناءً على الرتبة
        if st.session_state.role == "Admin":
            menu = ["📊 لوحة القيادة", "🤖 المساعد الذكي", "➕ طلب جديد", "📦 الورشة", "🧾 الحسابات", "📢 التسويق", "📲 واتساب التحصيل", "👥 العملاء", "👨‍💼 الفريق", "⚙️ الإعدادات"]
        else:
            menu = ["🏠 شاشتي الرئيسية", "🤖 المساعد الذكي"]
            
        choice = st.radio("التنقل", menu, label_visibility="collapsed")
        if st.button("🚪 تسجيل الخروج", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    # خريطة التوجيه (تأكد من مطابقتها لمفاتيح PAGES)
    nav_map = {
        "📊 لوحة القيادة": "dashboard", 
        "🤖 المساعد الذكي": "ai_assistant", 
        "➕ طلب جديد": "new_order",
        "📦 الورشة": "orders", 
        "🧾 الحسابات": "accounts", 
        "📢 التسويق": "marketing",
        "📲 واتساب التحصيل": "whatsapp", 
        "👥 العملاء": "clients", 
        "👨‍💼 الفريق": "employees", 
        "⚙️ الإعدادات": "categories"
    }

    st.markdown(f"#### 📍 {choice}")
    
    if choice == "🏠 شاشتي الرئيسية":
        role = st.session_state.role
        if role == "Designer": PAGES["designer"](conn, st.session_state.emp_name)
        elif role == "Technician": PAGES["tech"](conn, st.session_state.emp_name)
        elif role == "Installer": PAGES["installer"](conn, st.session_state.emp_name)
        else: st.info("لا توجد واجهة مخصصة لرتبتك حالياً.")
    else:
        selected_key = nav_map.get(choice)
        if selected_key in PAGES:
            # تمرير الكونكشن لجميع الصفحات لضمان عملها مع السبا بيز
            PAGES[selected_key](conn)

# --- 8. الانطلاق ---
if not st.session_state.logged_in:
    show_login_screen()
else:
    show_main_portal()
