import streamlit as st
import psycopg2
import warnings
from datetime import datetime
import os
import sys
from PIL import Image

# --- 🚀 1. حل جذري لمشاكل المسارات (Path Fix) ---
# نضمن أن بايثون يرى مجلدات web_ui و utils مهما كانت بيئة التشغيل
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# --- 2. تهيئة الإعدادات الأساسية ---
warnings.simplefilter('ignore', UserWarning)

st.set_page_config(
    page_title="نَسق ERP | النظام السحابي المطور", 
    page_icon="🎯", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 3. استيراد الشاشات بنظام الحماية (Safe Module Loading) ---
def load_system_pages():
    pages = {}
    
    # قائمة الوحدات البرمجية المطلوب استيرادها
    modules_to_import = {
        "dashboard": ("web_ui.dashboard", "render_dashboard"),
        "new_order": ("web_ui.new_order", "render_new_order"),
        "orders": ("web_ui.orders", "render_orders"),
        "accounts": ("web_ui.accounts", "render_accounts"),
        "clients": ("web_ui.clients", "render_clients"),
        "employees": ("web_ui.employees", "render_employees"),
        "categories": ("web_ui.categories", "render_categories"),
        "ai_assistant": ("web_ui.ai_assistant", "render_ai_assistant"),
        "designer": ("web_ui.designer", "render_designer"),
        "technician": ("web_ui.technician", "render_technician"),
        "installer": ("web_ui.installer", "render_installer")
    }

    for key, (mod_path, func_name) in modules_to_import.items():
        try:
            # استيراد ديناميكي لتجنب KeyError الكلي
            module = __import__(mod_path, fromlist=[func_name])
            pages[key] = getattr(module, func_name)
        except (ImportError, KeyError, AttributeError) as e:
            # في حال فشل ملف، نضع دالة بديلة تعرض رسالة خطأ بدلاً من انهيار الموقع
            pages[key] = lambda *args, **kwargs: st.error(f"⚠️ تعذر تحميل الشاشة ({key}). تأكد من وجود ملف {mod_path.split('.')[-1]}.py")
            
    return pages

PAGES = load_system_pages()

# --- 4. حقن الـ CSS المطور (التصميم الزجاجي) ---
def inject_creative_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    html, body, [data-testid="stSidebar"] *, .stMarkdown {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl; text-align: right;
    }
    [data-testid="stSidebar"] { background: #0c1221 !important; border-left: 1px solid rgba(56, 189, 248, 0.1); }
    header {visibility: hidden;}
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; }
    div.stButton > button { width: 100% !important; border-radius: 10px !important; }
    </style>
    """, unsafe_allow_html=True)

inject_creative_css()

# --- 5. الاتصال بقاعدة البيانات (بوابة Supabase) ---
@st.cache_resource(ttl=60) 
def init_connection():
    try:
        db_uri = "postgresql://postgres.jfqmcgicbdrhrtkhuwws:Nasaq268609@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"
        return psycopg2.connect(db_uri, sslmode="require", connect_timeout=15)
    except Exception as e:
        st.error(f"❌ خطأ في الاتصال بقاعدة البيانات: {e}")
        return None

conn = init_connection()

# --- 6. إدارة الجلسة (Session State) ---
if "logged_in" not in st.session_state:
    st.session_state.update({
        "logged_in": False,
        "emp_name": "",
        "role": "",
        "last_order_count": 0
    })

# --- 7. شاشة الدخول ---
def login_screen():
    st.write("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center; color: #38bdf8;'>NASAQ ERP</h1>", unsafe_allow_html=True)
        with st.form("login_form"):
            st.markdown("<p style='text-align: center; color: #94a3b8;'>نظام الإدارة المتكامل</p>", unsafe_allow_html=True)
            serial = st.text_input("رقم الموظف")
            password = st.text_input("كلمة المرور", type="password")
            if st.form_submit_button("دخول آمن 🚀"):
                if conn:
                    try:
                        conn.rollback()
                        cursor = conn.cursor()
                        cursor.execute("SELECT emp_name, role FROM employees WHERE serial_number = %s AND password = %s", (serial, password))
                        user = cursor.fetchone()
                        if user:
                            st.session_state.logged_in = True
                            st.session_state.emp_name = user[0]
                            st.session_state.role = user[1]
                            st.rerun()
                        else: st.error("بيانات الدخول غير صحيحة")
                    except Exception as e: st.error(f"خطأ في الاستعلام: {e}")

# --- 8. بوابات النظام ---
def admin_portal():
    with st.sidebar:
        st.markdown("<h2 style='color: #38bdf8; text-align: center;'>نَسق | المدير</h2>", unsafe_allow_html=True)
        st.divider()
        menu_options = [
            "📊 لوحة القيادة", "🤖 المساعد الذكي (Gemini)", "➕ طلب تشغيل جديد", 
            "📦 إدارة الورشة", "🧾 المالية", "👥 العملاء", 
            "👨‍💼 فريق العمل", "⚙️ الإعدادات"
        ]
        menu = st.radio("القائمة الرئيسية:", menu_options, label_visibility="collapsed")
        st.divider()
        if st.button("🚪 تسجيل الخروج"):
            st.session_state.logged_in = False
            st.rerun()

    # التوجيه بناءً على الاختيار
    if menu == "📊 لوحة القيادة": PAGES["dashboard"](conn)
    elif menu == "🤖 المساعد الذكي (Gemini)": PAGES["ai_assistant"]()
    elif menu == "➕ طلب تشغيل جديد": PAGES["new_order"](conn)
    elif menu == "📦 إدارة الورشة": PAGES["orders"](conn)
    elif menu == "🧾 المالية": PAGES["accounts"](conn)
    elif menu == "👥 العملاء": PAGES["clients"](conn)
    elif menu == "👨‍💼 فريق العمل": PAGES["employees"](conn)
    elif menu == "⚙️ الإعدادات": PAGES["categories"](conn)

def employee_portal():
    with st.sidebar:
        st.markdown(f"<div style='text-align:center; color:#38bdf8;'>👋 أهلاً {st.session_state.emp_name}</div>", unsafe_allow_html=True)
        st.divider()
        menu_emp = st.radio("القائمة:", ["🏠 الشاشة الرئيسية", "🤖 مساعد Gemini"])
        st.divider()
        if st.button("🚪 خروج"):
            st.session_state.logged_in = False
            st.rerun()
            
    if menu_emp == "🤖 مساعد Gemini": PAGES["ai_assistant"]()
    else:
        role = st.session_state.role
        if role == "Designer": PAGES["designer"](conn, st.session_state.emp_name)
        elif role == "Technician": PAGES["technician"](conn, st.session_state.emp_name)
        elif role == "Installer": PAGES["installer"](conn, st.session_state.emp_name)

# --- 9. التشغيل النهائي ---
if not st.session_state.logged_in:
    login_screen()
else:
    if st.session_state.role == "Admin":
        admin_portal()
    else:
        employee_portal()
