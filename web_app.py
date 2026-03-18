# web_app.py
import streamlit as st
import psycopg2
import warnings
from datetime import datetime

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

# إعدادات الصفحة الأساسية
st.set_page_config(page_title="NASAQ ERP - Cloud", page_icon="🌐", layout="wide")

# ✨ دالة تحسين الواجهة (CSS) المبدئية
def inject_custom_css():
    st.markdown("""
    <style>
    /* تحسين شكل الأزرار وتأثير الماوس */
    div.stButton > button:first-child {
        background-color: #0ea5e9;
        color: white;
        border-radius: 8px;
        border: none;
        transition: all 0.3s ease-in-out;
    }
    div.stButton > button:first-child:hover {
        background-color: #0284c7;
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(0,0,0,0.15);
    }
    /* تحسين حقول الإدخال لتكون أكثر عصرية */
    .stTextInput>div>div>input {
        border-radius: 8px;
        border: 1px solid #cbd5e1;
        padding: 0.5rem;
    }
    .stTextInput>div>div>input:focus {
        border-color: #0ea5e9;
        box-shadow: 0 0 0 1px #0ea5e9;
    }
    </style>
    """, unsafe_allow_html=True)

# تشغيل التحسينات البصرية
inject_custom_css()

# ✅ الاتصال بقاعدة البيانات
@st.cache_resource(ttl=60) 
def init_connection():
    try:
        # الرابط الرسمي لمشروعك في منطقة ap-northeast-1
        db_uri = "postgresql://postgres.jfqmcgicbdrhrtkhuwws:Nasaq268609@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"
        return psycopg2.connect(db_uri, sslmode="require", connect_timeout=10)
    except Exception as e:
        st.error(f"❌ عذراً، نواجه مشكلة تقنية في الاتصال بالسيرفر: {e}")
        return None

conn = init_connection()

# إدارة الجلسة (Session State)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.emp_name = ""
    st.session_state.role = ""
    st.session_state.last_order_count = 0

# --- شاشة تسجيل الدخول ---
def login_screen():
    # مساحة بيضاء علوية للترتيب
    st.write("<br>", unsafe_allow_html=True)
    
    st.markdown("<h1 style='text-align: center; color: #0ea5e9;'>مؤسسة نسق للدعاية والإعلان</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: #64748b;'>بوابة الإدارة السحابية ☁️</h4>", unsafe_allow_html=True)
    st.write("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.form("login_form"):
            serial = st.text_input("👤 الرقم الوظيفي")
            password = st.text_input("🔑 كلمة المرور", type="password")
            st.write("<br>", unsafe_allow_html=True)
            if st.form_submit_button("تسجيل الدخول", use_container_width=True):
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
                    st.warning("⚠️ جاري محاولة تأمين الاتصال بالسيرفر.. انتظر لحظة.")

# --- نظام الإشعارات اللحظي ---
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

# --- واجهة المدير (Admin) ---
def admin_portal():
    with st.sidebar:
        st.markdown(f"### 👋 أهلاً بك يا مدير: {st.session_state.emp_name}")
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

# --- واجهة الموظفين ---
def employee_portal():
    with st.sidebar:
        st.markdown(f"### 👋 مرحباً: {st.session_state.emp_name}")
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
