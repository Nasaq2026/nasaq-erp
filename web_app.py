# web_app.py
import streamlit as st
import psycopg2
import warnings
from datetime import datetime
import os
from PIL import Image

# استيراد الشاشات من مجلد web_ui
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

warnings.simplefilter('ignore', UserWarning)

# إعدادات الصفحة
st.set_page_config(
    page_title="نسق ERP | إدارة متكاملة", 
    page_icon="🎯", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 🖼️ دالة تحميل اللوجو ---
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

# --- ✨ حقن CSS المطور (Neon Glass Design) ---
def inject_creative_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');

    /* التنسيق العام والخط */
    html, body, [data-testid="stSidebar"] *, .stMarkdown {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl; 
        text-align: right;
    }

    /* --- 🌑 القائمة الجانبية (Dark Sidebar) --- */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #090e1a 0%, #0c1221 100%) !important;
        border-left: 1px solid rgba(56, 189, 248, 0.15);
    }

    /* --- 🚫 إزالة الدوائر البيضاء الافتراضية --- */
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label div[data-testid="stRadioButtonCustomObject"] {
        display: none !important;
    }

    /* --- 💖 تنسيق الأزرار (Glassmorphism Effect) --- */
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
        color: #94a3b8 !important; /* لون رمادي مزرق هادئ */
        background-color: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        padding: 14px 20px !important;
        border-radius: 12px !important;
        margin-bottom: 10px !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        display: flex;
        align-items: center;
        width: 100% !important;
        font-weight: 500;
        font-size: 15px;
    }

    /* --- 💡 تأثير الماوس (إضاءة نيون) --- */
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
        background-color: rgba(56, 189, 248, 0.08) !important;
        border-color: rgba(56, 189, 248, 0.3) !important;
        color: #f8fafc !important;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.15);
        transform: translateY(-2px); /* حركة بسيطة للأعلى */
    }

    /* --- 🎯 عند اختيار العنصر (Active State) --- */
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[data-selected="true"] {
        background: rgba(56, 189, 248, 0.1) !important;
        border-color: #38bdf8 !important; /* حد أزرق نيون */
        color: white !important;
        font-weight: 600;
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.3), inset 0 0 10px rgba(56, 189, 248, 0.1);
    }

    /* --- 📅 تنسيق التاريخ --- */
    .date-container {
        color: #64748b;
        font-size: 13px;
        text-align: center;
        margin-bottom: 20px;
    }

    /* 🔴 زر تسجيل الخروج العصري */
    .stSidebar div.stButton > button {
        background: rgba(239, 68, 68, 0.1) !important;
        color: #ef4444 !important;
        border: 1px solid rgba(239, 68, 68, 0.2) !important;
        width: 100% !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        margin-top: 25px;
    }
    
    .stSidebar div.stButton > button:hover {
        background: #ef4444 !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3);
    }

    /* إخفاء شعار Streamlit العلوي */
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

inject_creative_css()

# ✅ الربط بقاعدة البيانات (كما هو في كودك)
@st.cache_resource(ttl=60) 
def init_connection():
    try:
        db_uri = "postgresql://postgres.jfqmcgicbdrhrtkhuwws:Nasaq268609@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"
        return psycopg2.connect(db_uri, sslmode="require", connect_timeout=10)
    except Exception as e:
        st.error(f"❌ خطأ في الاتصال: {e}")
        return None

conn = init_connection()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.emp_name = ""
    st.session_state.role = ""

# دالة عرض اللوجو
def show_logo(width=200):
    if LOGO_IMG:
        st.image(LOGO_IMG, width=width)
    else:
        st.markdown("<h2 style='color: #38bdf8; text-align: center;'>NASAQ ERP</h2>", unsafe_allow_html=True)

# شاشة الدخول (Login)
def login_screen():
    st.write("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        show_logo(width=300)
        st.write("<br>", unsafe_allow_html=True)
        with st.form("login_form"):
            st.markdown("<h3 style='text-align: center;'>تسجيل الدخول</h3>", unsafe_allow_html=True)
            serial = st.text_input("رقم الموظف", placeholder="A-1001")
            password = st.text_input("كلمة المرور", type="password")
            if st.form_submit_button("دخول آمن", use_container_width=True):
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
                        else: st.error("بيانات غير صحيحة")
                    except: st.error("خطأ تقني")

# بوابة المدير (Admin Portal)
def admin_portal():
    with st.sidebar:
        show_logo(width=220)
        st.markdown(f"<div class='date-container'>{datetime.now().strftime('%Y-%m-%d | %H:%M')}</div>", unsafe_allow_html=True)
        st.divider()
        
        # --- القائمة بالأيقونات الجديدة (المطابقة لطلبك) ---
        menu_options = [
            "📊 لوحة القيادة",
            "➕ طلب تشغيل جديد",
            "📦 إدارة الورشة", 
            "🧾 الفواتير والمالية",
            "👥 إدارة العملاء",
            "💬 تواصل وواتساب",
            "📢 حملات تسويقية",
            "👨‍💼 إدارة الفريق",
            "⚙️ إعدادات النظام"
        ]
        
        # استخدام st.radio كقائمة أزرار (كما طلبت)
        menu = st.radio("القائمة الرئيسية:", menu_options)
        
        st.divider()
        if st.button("🚪 تسجيل الخروج"):
            st.session_state.logged_in = False
            st.rerun()

    # تنفيذ الصفحات
    if menu == "📊 لوحة القيادة": render_dashboard(conn)
    elif menu == "➕ طلب تشغيل جديد": render_new_order(conn)
    elif menu == "📦 إدارة الورشة": render_orders(conn)
    elif menu == "🧾 الفواتير والمالية": render_accounts(conn)
    elif menu == "👥 إدارة العملاء": render_clients(conn)
    elif menu == "💬 تواصل وواتساب": render_communication(conn)
    elif menu == "📢 حملات تسويقية": render_marketing(conn)
    elif menu == "👨‍💼 إدارة الفريق": render_employees(conn)
    elif menu == "⚙️ إعدادات النظام": render_categories(conn)

# بوابة الموظف (Employee Portal)
def employee_portal():
    with st.sidebar:
        show_logo(width=180)
        st.divider()
        st.markdown(f"#### 👋 {st.session_state.emp_name}")
        st.caption(f"قسم: {st.session_state.role}")
        st.divider()
        if st.button("🚪 تسجيل الخروج"):
            st.session_state.logged_in = False
            st.rerun()
    
    if st.session_state.role == "Designer": render_designer(conn, st.session_state.emp_name)
    elif st.session_state.role == "Technician": render_technician(conn, st.session_state.emp_name)
    elif st.session_state.role == "Installer": render_installer(conn, st.session_state.emp_name)

# توجيه الدخول
if not st.session_state.logged_in:
    login_screen()
else:
    if st.session_state.role == "Admin": admin_portal()
    else: employee_portal()
