# web_app.py
import streamlit as st
import psycopg2
import warnings
from datetime import datetime
import os # لإدارة مسارات الملفات

# استيراد الشاشات من مجلد web_ui
from web_ui.dashboard import render_dashboard
from web_ui.new_order import render_new_order
from web_ui.orders import render_orders
from web_ui.accounts import render_accounts
from web_ui.clients import render_clients
from web_ui.communication import render_communication
from web_ui.marketing import render_marketing
from web_ui.employees import render_employees
from web_ui.designers import render_designers
from web_ui.categories import render_categories
from web_ui.calculator import render_calculator
from web_ui.invoices import render_invoices
from web_ui.designer import render_designer
from web_ui.technician import render_technician
from web_ui.installer import render_installer

warnings.simplefilter('ignore', UserWarning)

# ✅ إعدادات الصفحة الاحترافية (تغيير الأيقونة والعنوان)
st.set_page_config(
    page_title="نسق ERP | بوابة الإدارة السحابية", 
    page_icon="🌐", # يمكنك وضع رابط لوجو صغير هنا أيضاً كـ Favicon
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🔗 إعداد رابط اللوجو (استبدله برابط لوجو مؤسسة نسق الحقيقي)
# يمكنك رفع اللوجو على GitHub واستخدام اسمه مباشرة إذا كان في نفس المجلد
LOGO_URL = "https://via.placeholder.com/200x80.png?text=NASAQ+LOGO" 
# إذا رفعت ملف اسمه logo.png في GitHub، اجعل السطر فوق هكذا:
# LOGO_URL = os.path.join(os.path.dirname(__file__), 'logo.png')


# ✨ دالة حقن الـ CSS الاحترافي (الفخامة كلها هنا)
def inject_creative_css():
    st.markdown("""
    <style>
    /* --- استيراد خط عربي احترافي (Cairo) --- */
    @import url('https://fonts.googleapis.com/css2?Cairo:wght@400;600;700&display=swap');

    html, body, [data-testid="stSidebar"], .stMarkdown {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl; /* توجيه التطبيق لليمين */
        text-align: right;
    }

    /* --- تجميل الأزرار الرئيسية (Nasaq Style) --- */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
        color: white;
        border-radius: 50px; /* حواف دائرية بالكامل */
        border: none;
        padding: 10px 24px;
        font-weight: 600;
        font-size: 16px;
        transition: all 0.3s ease-in-out;
        box-shadow: 0 4px 6px rgba(14, 165, 233, 0.2);
    }
    
    /* تأثيرات الماوس على الزراير */
    div.stButton > button:first-child:hover {
        background: linear-gradient(135deg, #0284c7 0%, #0ea5e9 100%);
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 8px 15px rgba(14, 165, 233, 0.4);
    }

    /* --- تجميل خانات الإدخال (Inputs) --- */
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stTextArea>div>div>textarea {
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        background-color: #ffffff;
        padding: 12px;
        transition: all 0.2s;
    }
    .stTextInput>div>div>input:focus {
        border-color: #0ea5e9;
        box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.1);
    }

    /* --- تجميل الشريط الجانبي (Sidebar) --- */
    [data-testid="stSidebar"] {
        background-color: #F8FAFC;
        border-left: 1px solid #e2e8f0;
    }
    
    /* تجميل عناوين القوائم في السايدبار */
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
        color: #1e293b;
        font-weight: 600;
        padding: 10px;
        border-radius: 8px;
        transition: background 0.2s;
    }
    
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[data-selected="true"] {
        background-color: rgba(14, 165, 233, 0.1);
        color: #0284c7 !important;
    }

    /* --- تجميل كروت البيانات (Metric/Cards) --- */
    [data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 15px;
        border-radius: 16px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }

    /* --- تجميل شكل الفورم (Login box) --- */
    [data-testid="stForm"] {
        background-color: #ffffff;
        padding: 30px;
        border-radius: 20px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
    }
    
    /* إخفاء شريط Streamlit المزعج في الأعلى */
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# تشغيل الـ CSS الاحترافي
inject_creative_css()

# ✅ الاتصال بقاعدة البيانات (كما هو)
@st.cache_resource(ttl=60) 
def init_connection():
    try:
        db_uri = "postgresql://postgres.jfqmcgicbdrhrtkhuwws:Nasaq268609@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"
        return psycopg2.connect(db_uri, sslmode="require", connect_timeout=10)
    except Exception as e:
        st.error(f"❌ عذراً، هناك مشكلة في الاتصال: {e}")
        return None

conn = init_connection()

# إدارة الجلسة
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.emp_name = ""
    st.session_state.role = ""
    st.session_state.last_order_count = 0

# --- شاشة تسجيل الدخول المطورة ---
def login_screen():
    st.write("<br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        # 🖼️ عرض اللوجو في المنتصف
        st.image(LOGO_URL, use_container_width=True)
        st.write("<br>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            st.markdown("<h3 style='text-align: center; color: #1e293b;'>تسجيل الدخول بوابة الإدارة</h3>", unsafe_allow_html=True)
            st.write("<br>", unsafe_allow_html=True)
            
            serial = st.text_input("👤 الرقم الوظيفي", placeholder="أدخل رقمك الوظيفي")
            password = st.text_input("🔑 كلمة المرور", type="password", placeholder="أدخل كلمة المرور")
            st.write("<br>", unsafe_allow_html=True)
            
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
                            cursor.execute("SELECT COUNT(*) FROM orders")
                            st.session_state.last_order_count = cursor.fetchone()[0]
                            st.rerun()
                        else:
                            st.error("❌ بيانات الدخول غير صحيحة")
                    except Exception as e:
                        st.error(f"خطأ في قاعدة البيانات: {e}")
                else:
                    st.warning("⚠️ جاري تأمين الاتصال بالسيرفر..")

# --- باقي كود البوابات كما هو ---
def check_notifications():
    if conn:
        try:
            conn.rollback()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM orders")
            current_count = cursor.fetchone()[0]
            if current_count > st.session_state.last_order_count:
                st.toast(f"🔔 تنبيه: تم إضافة طلبات جديدة!", icon="🚨")
                st.session_state.last_order_count = current_count
        except: pass

def admin_portal():
    with st.sidebar:
        # 🖼️ عرض اللوجو أعلى الشريط الجانبي
        st.image(LOGO_URL, use_container_width=True)
        st.divider()
        st.markdown(f"#### 👋 مرحباً يا مدير: **{st.session_state.emp_name}**")
        st.divider()
        menu = st.radio("القائمة الرئيسية:", [
            "📊 لوحة القيادة", "➕ طلب تشغيل جديد", "📦 إدارة الطلبات (الورشة)", 
            "🧾 سجل الفواتير", "💰 التقارير المالية", "👥 إدارة العملاء (CRM)",
            "💬 المديونيات والواتساب", "📢 التسويق وحملات التهاني", "🧮 حاسبة الأسعار والهدر",
            "👨‍🎨 إدارة المصممين", "👨‍💼 إدارة الموظفين", "⚙️ إعدادات الأقسام"
        ])
        st.divider()
        if st.button("🚪 تسجيل الخروج", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    if menu == "📊 لوحة القيادة": render_dashboard(conn)
    elif menu == "➕ طلب تشغيل جديد": render_new_order(conn)
    elif menu == "📦 إدارة الطلبات (الورشة)": render_orders(conn)
    elif menu == "🧾 سجل الفواتير": render_invoices(conn)
    elif menu == "💰 التقارير المالية": render_accounts(conn)
    elif menu == "👥 إدارة العملاء (CRM)": render_clients(conn)
    elif menu == "💬 المديونيات والواتساب": render_communication(conn)
    elif menu == "📢 التسويق وحملات التهاني": render_marketing(conn)
    elif menu == "🧮 حاسبة الأسعار والهدر": render_calculator(conn)
    elif menu == "👨‍🎨 إدارة المصممين": render_designers(conn)
    elif menu == "👨‍💼 إدارة الموظفين": render_employees(conn)
    elif menu == "⚙️ إعدادات الأقسام": render_categories(conn)

def employee_portal():
    with st.sidebar:
        # 🖼️ عرض اللوجو أعلى الشريط الجانبي للموظفين
        st.image(LOGO_URL, use_container_width=True)
        st.divider()
        st.markdown(f"#### 👋 مرحباً: **{st.session_state.emp_name}**")
        st.markdown(f"**القسم:** {st.session_state.role}")
        st.divider()
        if st.button("🚪 تسجيل الخروج", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    if st.session_state.role == "Designer": render_designer(conn, st.session_state.emp_name)
    elif st.session_state.role == "Technician": render_technician(conn, st.session_state.emp_name)
    elif st.session_state.role == "Installer": render_installer(conn, st.session_state.emp_name)

# --- تشغيل التطبيق ---
if not st.session_state.logged_in:
    login_screen()
else:
    check_notifications()
    if st.session_state.role == "Admin": admin_portal()
    else: employee_portal()
