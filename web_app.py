# web_app.py
import streamlit as st
import psycopg2
import warnings
from datetime import datetime
import os
import sys
from PIL import Image

# --- 💡 حل مشكلة المسارات لضمان رؤية المجلدات ---
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# 1. تهيئة الإعدادات الأساسية
warnings.simplefilter('ignore', UserWarning)

st.set_page_config(
    page_title="نسق ERP | إدارة متكاملة", 
    page_icon="🎯", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. استيراد الشاشات مع نظام حماية من الانهيار (Safe Import)
try:
    from web_ui.dashboard import render_dashboard
    from web_ui.new_order import render_new_order
    from web_ui.orders import render_orders
    from web_ui.accounts import render_accounts
    from web_ui.clients import render_clients
    from web_ui.communication import render_communication
    from web_ui.marketing import render_marketing
    from web_ui.employees import render_employees
    from web_ui.categories import render_categories
    from web_ui.calculator import render_calculator
    from web_ui.designer import render_designer
    from web_ui.technician import render_technician
    from web_ui.installer import render_installer
    
    # محاولة استيراد المساعد الذكي، لو فشل لن ينهار البرنامج
    HAS_AI = False
    try:
        from web_ui.ai_assistant import render_ai_assistant
        HAS_AI = True
    except ImportError:
        HAS_AI = False

except ImportError as e:
    st.error(f"❌ فشل استيراد ملفات النظام الأساسية: {e}")
    st.stop()

# 3. تحميل اللوجو
@st.cache_data
def load_logo():
    try:
        logo_path = os.path.join(current_dir, "logo.png")
        if os.path.exists(logo_path):
            return Image.open(logo_path)
        return None
    except:
        return None

LOGO_IMG = load_logo()

# 4. الـ CSS المطور
def inject_creative_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    html, body, [data-testid="stSidebar"] *, .stMarkdown {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl; 
        text-align: right;
    }
    [data-testid="stSidebar"] { background: #0c1221 !important; }
    header {visibility: hidden;}
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

inject_creative_css()

# 5. تهيئة الـ Session State
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.emp_name = ""
    st.session_state.role = ""

# 6. الاتصال بقاعدة البيانات
@st.cache_resource(ttl=60) 
def init_connection():
    try:
        db_uri = "postgresql://postgres.jfqmcgicbdrhrtkhuwws:Nasaq268609@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"
        return psycopg2.connect(db_uri, sslmode="require", connect_timeout=10)
    except Exception as e:
        st.error(f"❌ خطأ في قاعدة البيانات: {e}")
        return None

conn = init_connection()

# 7. شاشة الدخول
def login_screen():
    st.write("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        if LOGO_IMG: st.image(LOGO_IMG, width=300)
        else: st.markdown("<h2 style='color: #38bdf8; text-align: center;'>NASAQ ERP</h2>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            st.markdown("<h3 style='text-align: center;'>تسجيل الدخول</h3>", unsafe_allow_html=True)
            serial = st.text_input("رقم الموظف")
            password = st.text_input("كلمة المرور", type="password")
            if st.form_submit_button("دخول آمن", use_container_width=True):
                if conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT emp_name, role FROM employees WHERE serial_number = %s AND password = %s", (serial, password))
                    user = cursor.fetchone()
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.emp_name = user[0]
                        st.session_state.role = user[1]
                        st.rerun()
                    else: st.error("بيانات الدخول غير صحيحة")

# 8. بوابات النظام
def admin_portal():
    with st.sidebar:
        if LOGO_IMG: st.image(LOGO_IMG, width=200)
        st.divider()
        menu_options = ["📊 لوحة القيادة"]
        
        if HAS_AI: menu_options.append("🤖 المساعد الذكي (Gemini)")
        
        menu_options += [
            "➕ طلب تشغيل جديد", "📦 إدارة الورشة", "🧾 الفواتير والمالية", 
            "👥 إدارة العملاء", "💬 تواصل وواتساب", "📢 حملات تسويقية", 
            "👨‍💼 إدارة الفريق", "⚙️ إعدادات النظام"
        ]
        menu = st.radio("القائمة الرئيسية:", menu_options)
        
        if st.button("🚪 تسجيل الخروج", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    # نظام التنقل
    if menu == "📊 لوحة القيادة": render_dashboard(conn)
    elif menu == "🤖 المساعد الذكي (Gemini)" and HAS_AI: render_ai_assistant()
    elif menu == "➕ طلب تشغيل جديد": render_new_order(conn)
    elif menu == "📦 إدارة الورشة": render_orders(conn)
    elif menu == "🧾 الفواتير والمالية": render_accounts(conn)
    elif menu == "👥 إدارة العملاء": render_clients(conn)
    elif menu == "💬 تواصل وواتساب": render_communication(conn)
    elif menu == "📢 حملات تسويقية": render_marketing(conn)
    elif menu == "👨‍💼 إدارة الفريق": render_employees(conn)
    elif menu == "⚙️ إعدادات النظام": render_categories(conn)

def employee_portal():
    with st.sidebar:
        st.markdown(f"<div style='text-align:center; color:#38bdf8;'>👋 أهلاً {st.session_state.emp_name}</div>", unsafe_allow_html=True)
        options = ["🏠 الشاشة الرئيسية"]
        if HAS_AI: options.append("🤖 مساعد Gemini")
        menu_emp = st.radio("القائمة:", options)
        
        if st.button("🚪 تسجيل الخروج", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
            
    if menu_emp == "🤖 مساعد Gemini" and HAS_AI:
        render_ai_assistant()
    else:
        if st.session_state.role == "Designer": render_designer(conn, st.session_state.emp_name)
        elif st.session_state.role == "Technician": render_technician(conn, st.session_state.emp_name)
        elif st.session_state.role == "Installer": render_installer(conn, st.session_state.emp_name)

# 9. التشغيل النهائي
if not st.session_state.logged_in:
    login_screen()
else:
    if st.session_state.role == "Admin": admin_portal()
    else: employee_portal()
