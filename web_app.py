# web_app.py
import streamlit as st
import psycopg2
import warnings
from datetime import datetime
import os
from PIL import Image

# 1. تهيئة الإعدادات الأساسية
warnings.simplefilter('ignore', UserWarning)

st.set_page_config(
    page_title="نسق ERP | إدارة متكاملة", 
    page_icon="🎯", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. استيراد الشاشات من مجلد web_ui
# ملاحظة: تأكد أن مجلد web_ui يحتوي على ملف __init__.py (حتى لو فارغ) ليعتبره بايثون حزمة
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
except ImportError as e:
    st.error(f"❌ فشل استيراد أحد ملفات الواجهة: {e}")
    st.info("تأكد أن جميع الملفات موجودة داخل مجلد web_ui وأن أسماءها تطابق الكود تماماً (Small Letters).")

# 3. تحميل اللوجو
@st.cache_data
def load_logo():
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(current_dir, "logo.png")
        if os.path.exists(logo_path):
            return Image.open(logo_path)
        return None
    except:
        return None

LOGO_IMG = load_logo()

# 4. حقن الـ CSS المطور (تصميم زجاجي + نصوص بيضاء ناصعة)
def inject_creative_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');

    html, body, [data-testid="stSidebar"] *, .stMarkdown {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl; 
        text-align: right;
    }

    [data-testid="stSidebar"] {
        background: #0c1221 !important;
        border-left: 1px solid rgba(56, 189, 248, 0.1);
    }

    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label div[data-testid="stRadioButtonCustomObject"] {
        display: none !important;
    }

    /* نصوص القائمة الجانبية باللون الأبيض الصريح */
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p {
        color: #ffffff !important;
        font-size: 16px !important;
        font-weight: 600 !important;
    }

    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
        background-color: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        padding: 14px 20px !important;
        border-radius: 12px !important;
        margin-bottom: 12px !important;
        display: flex;
        align-items: center;
        transition: 0.3s;
        width: 100% !important;
    }

    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[data-selected="true"] {
        background: rgba(56, 189, 248, 0.15) !important;
        border-color: #38bdf8 !important;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.2);
    }

    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

inject_creative_css()

# 5. تهيئة الـ Session State
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.emp_name = ""
    st.session_state.role = ""
    st.session_state.last_order_count = 0

# 6. الربط بقاعدة البيانات
@st.cache_resource(ttl=60) 
def init_connection():
    try:
        db_uri = "postgresql://postgres.jfqmcgicbdrhrtkhuwws:Nasaq268609@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"
        return psycopg2.connect(db_uri, sslmode="require", connect_timeout=10)
    except Exception as e:
        st.error(f"❌ خطأ في الاتصال بقاعدة البيانات: {e}")
        return None

conn = init_connection()

def show_logo(width=200):
    if LOGO_IMG:
        st.image(LOGO_IMG, width=width)
    else:
        st.markdown("<h2 style='color: #38bdf8; text-align: center;'>NASAQ ERP</h2>", unsafe_allow_html=True)

# 7. شاشة الدخول
def login_screen():
    st.write("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        show_logo(width=300)
        with st.form("login_form"):
            st.markdown("<h3 style='text-align: center;'>تسجيل الدخول</h3>", unsafe_allow_html=True)
            serial = st.text_input("رقم الموظف")
            password = st.text_input("كلمة المرور", type="password")
            if st.form_submit_button("دخول آمن", width="stretch"):
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
                    except Exception as e:
                        st.error(f"خطأ في الاستعلام: {e}")

# 8. بوابات النظام (Admin / Employees)
def admin_portal():
    with st.sidebar:
        show_logo(width=220)
        st.divider()
        menu_options = [
            "📊 لوحة القيادة", "➕ طلب تشغيل جديد", "📦 إدارة الورشة", 
            "🧾 الفواتير والمالية", "👥 إدارة العملاء", "💬 تواصل وواتساب",
            "📢 حملات تسويقية", "👨‍💼 إدارة الفريق", "🧮 حاسبة التكاليف", "⚙️ إعدادات النظام"
        ]
        menu = st.radio("القائمة:", menu_options, label_visibility="collapsed")
        st.divider()
        if st.button("🚪 تسجيل الخروج", width="stretch"):
            st.session_state.logged_in = False
            st.rerun()

    # التوجيه بناءً على الخيار
    if menu == "📊 لوحة القيادة": render_dashboard(conn)
    elif menu == "➕ طلب تشغيل جديد": render_new_order(conn)
    elif menu == "📦 إدارة الورشة": render_orders(conn)
    elif menu == "🧾 الفواتير والمالية": render_accounts(conn)
    elif menu == "👥 إدارة العملاء": render_clients(conn)
    elif menu == "💬 تواصل وواتساب": render_communication(conn)
    elif menu == "📢 حملات تسويقية": render_marketing(conn)
    elif menu == "👨‍💼 إدارة الفريق": render_employees(conn)
    elif menu == "🧮 حاسبة التكاليف": render_calculator(conn)
    elif menu == "⚙️ إعدادات النظام": render_categories(conn)

def employee_portal():
    with st.sidebar:
        show_logo(width=180)
        st.markdown(f"<div style='text-align:center;'>👋 أهلاً {st.session_state.emp_name}</div>", unsafe_allow_html=True)
        st.divider()
        if st.button("🚪 تسجيل الخروج", width="stretch"):
            st.session_state.logged_in = False
            st.rerun()
            
    if st.session_state.role == "Designer": render_designer(conn, st.session_state.emp_name)
    elif st.session_state.role == "Technician": render_technician(conn, st.session_state.emp_name)
    elif st.session_state.role == "Installer": render_installer(conn, st.session_state.emp_name)

# 9. التشغيل
if not st.session_state.logged_in:
    login_screen()
else:
    if st.session_state.role == "Admin": admin_portal()
    else: employee_portal()
