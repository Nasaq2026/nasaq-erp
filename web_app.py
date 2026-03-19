# web_app.py
import streamlit as st
import psycopg2
import warnings
from datetime import datetime
import os
import sys
from PIL import Image

# --- 🚀 1. حل مشكلة المسارات (Path Fix) ---
# نضمن أن بايثون يرى مجلدات web_ui و utils مهما كان مكان التشغيل
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# --- 2. إعدادات الصفحة ---
warnings.simplefilter('ignore', UserWarning)
st.set_page_config(
    page_title="نَسق ERP | النظام السحابي", 
    page_icon="🎯", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 3. استيراد الشاشات (مع فحص الأخطاء) ---
def safe_import():
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
        from web_ui.ai_assistant import render_ai_assistant
        
        return {
            "dashboard": render_dashboard,
            "new_order": render_new_order,
            "orders": render_orders,
            "accounts": render_accounts,
            "clients": render_clients,
            "comm": render_communication,
            "marketing": render_marketing,
            "employees": render_employees,
            "categories": render_categories,
            "calc": render_calculator,
            "designer": render_designer,
            "tech": render_technician,
            "installer": render_installer,
            "ai": render_ai_assistant
        }
    except ImportError as e:
        st.error(f"❌ خطأ في تحميل ملفات النظام: {e}")
        st.info("💡 نصيحة: تأكد من وجود ملف فارغ باسم __init__.py داخل مجلد web_ui ومجلد utils")
        st.stop()

PAGES = safe_import()

# --- 4. الاتصال بقاعدة البيانات ---
@st.cache_resource(ttl=60)
def init_connection():
    try:
        # رابط الاتصال المباشر بـ Supabase
        db_uri = "postgresql://postgres.jfqmcgicbdrhrtkhuwws:Nasaq268609@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"
        return psycopg2.connect(db_uri, sslmode="require", connect_timeout=15)
    except Exception as e:
        st.error(f"❌ فشل الاتصال بالسحابة: {e}")
        return None

conn = init_connection()

# --- 5. نظام تسجيل الدخول ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.emp_name = ""
    st.session_state.role = ""

def login_screen():
    st.write("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center; color: #38bdf8;'>NASAQ ERP</h1>", unsafe_allow_html=True)
        with st.form("login_form"):
            serial = st.text_input("رقم الموظف (مثلاً: A-1001)")
            password = st.text_input("كلمة المرور", type="password")
            if st.form_submit_button("دخول آمن 🚀", use_container_width=True):
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

# --- 6. بوابات النظام بناءً على الصلاحيات ---
def main_app():
    with st.sidebar:
        st.markdown(f"### 🎯 نَسق | {st.session_state.role}")
        st.write(f"أهلاً، {st.session_state.emp_name}")
        st.divider()
        
        if st.session_state.role == "Admin":
            menu_options = [
                "📊 لوحة القيادة", "🤖 المساعد الذكي", "➕ طلب تشغيل جديد", 
                "📦 إدارة الورشة", "🧾 المالية", "👥 إدارة العملاء", 
                "👨‍💼 إدارة الفريق", "⚙️ الإعدادات"
            ]
        else:
            menu_options = ["🏠 شاشتي الرئيسية", "🤖 المساعد الذكي"]
            
        menu = st.sidebar.radio("القائمة:", menu_options)
        
        st.divider()
        if st.button("🚪 خروج"):
            st.session_state.logged_in = False
            st.rerun()

    # التوجيه (Routing)
    if menu == "📊 لوحة القيادة": PAGES["dashboard"](conn)
    elif menu == "🤖 المساعد الذكي": PAGES["ai"]()
    elif menu == "➕ طلب تشغيل جديد": PAGES["new_order"](conn)
    elif menu == "📦 إدارة الورشة": PAGES["orders"](conn)
    elif menu == "🧾 المالية": PAGES["accounts"](conn)
    elif menu == "👥 إدارة العملاء": PAGES["clients"](conn)
    elif menu == "👨‍💼 إدارة الفريق": PAGES["employees"](conn)
    elif menu == "⚙️ الإعدادات": PAGES["categories"](conn)
    
    # واجهة الموظفين
    elif menu == "🏠 شاشتي الرئيسية":
        role = st.session_state.role
        if role == "Designer": PAGES["designer"](conn, st.session_state.emp_name)
        elif role == "Technician": PAGES["tech"](conn, st.session_state.emp_name)
        elif role == "Installer": PAGES["installer"](conn, st.session_state.emp_name)

# التشغيل
if not st.session_state.logged_in:
    login_screen()
else:
    main_app()
