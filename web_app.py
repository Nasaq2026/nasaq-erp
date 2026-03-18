# web_app.py
import streamlit as st
import psycopg2
import warnings
from datetime import datetime
import os
from PIL import Image

# استيراد الشاشات
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

st.set_page_config(
    page_title="نسق ERP | إدارة متكاملة", 
    page_icon="🎯", 
    layout="wide",
    initial_sidebar_state="expanded"
)

def inject_creative_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');

    html, body, .stMarkdown {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl; 
        text-align: right;
    }

    /* --- 🌑 القائمة الجانبية (Dark Sidebar) --- */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important; 
    }

    /* --- 🚫 إزالة الدوائر البيضاء تماماً --- */
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] [data-testid="stWidgetLabel"] {
        display: none; /* إخفاء كلمة 'القائمة الرئيسية' لزيادة النظافة */
    }
    
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p {
        font-size: 16px !important;
        font-weight: 600 !important;
    }

    /* إخفاء الدائرة (الراديو) نفسه */
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label [data-testid="stRadioButtonCustomObject"] {
        display: none !important;
    }

    /* --- ✨ تنسيق النص (أسود عند الاختيار وأبيض ناصع بدلاً من الرمادي) --- */
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
        color: #f8fafc !important; /* أبيض ناصع في الحالة العادية */
        background-color: transparent !important;
        padding: 10px 15px !important;
        border-radius: 10px !important;
        margin-bottom: 5px !important;
        transition: all 0.3s ease;
        border: 1px solid transparent !important;
    }

    /* --- 💡 تأثير الماوس (إضاءة) --- */
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: #38bdf8 !important; /* لون سماوي مضيء */
        transform: translateX(-5px);
    }

    /* --- 🎯 عند اختيار العنصر (يصبح النص أسود والخلفية بيضاء/سماوية) --- */
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[data-selected="true"] {
        background-color: #38bdf8 !important; /* خلفية سماوية قوية */
        color: #000000 !important; /* النص يصبح أسود واضح جداً */
        box-shadow: 0 4px 15px rgba(56, 189, 248, 0.4) !important;
        font-weight: 700 !important;
    }

    /* إخفاء الهيدر */
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

inject_creative_css()

# (بقية كود الاتصال والدخول كما هو في ملفك الأصلي)
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

def admin_portal():
    with st.sidebar:
        st.markdown("<h2 style='color: #38bdf8; text-align: center;'>NASAQ ERP</h2>", unsafe_allow_html=True)
        st.divider()
        
        menu_options = [
            "📊 لوحة القيادة", "➕ طلب تشغيل جديد", "📦 إدارة الورشة", 
            "🧾 الفواتير والمالية", "👥 إدارة العملاء", "💬 تواصل وواتساب",
            "📢 حملات تسويقية", "👨‍💼 إدارة الفريق", "🧮 حاسبة التكاليف", "⚙️ إعدادات النظام"
        ]
        
        # الراديو الآن سيعمل كقائمة أزرار بدون دوائر
        menu = st.radio("", menu_options)
        
        st.divider()
        if st.button("🚪 تسجيل الخروج", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    # التوجيه بناءً على الاختيار
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

# (كود الـ main والدخول)
if not st.session_state.logged_in:
    # شاشة الدخول (Login)
    st.title("دخول النظام")
    with st.form("login"):
        user = st.text_input("رقم الموظف")
        pwd = st.text_input("كلمة المرور", type="password")
        if st.form_submit_button("دخول"):
             if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT emp_name, role FROM employees WHERE serial_number = %s AND password = %s", (user, pwd))
                res = cursor.fetchone()
                if res:
                    st.session_state.logged_in = True
                    st.session_state.emp_name = res[0]
                    st.session_state.role = res[1]
                    st.rerun()
else:
    admin_portal()
