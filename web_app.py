# web_app.py
import streamlit as st
import psycopg2
import warnings
from datetime import datetime

# 🔴 استيراد كافة الشاشات من مجلد web_ui
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

# إعدادات الصفحة
st.set_page_config(page_title="NASAQ ERP - Cloud", page_icon="🌐", layout="wide")

# ✅ الحل المستقر والنهائي للاتصال بسحابة Supabase (عبر الـ Pooler الموحد)
@st.cache_resource(ttl=60) 
def init_connection():
    try:
        # استخدام الـ Connection Pooler الخاص بـ AWS eu-central-1 (المنطقة الأقرب للسعودية)
        return psycopg2.connect(
            dbname="postgres", 
            user="postgres", 
            password="Nasaq268609", 
            host="aws-0-eu-central-1.pooler.supabase.com", # الـ Host الأكثر استقراراً للسحاب
            port="5432", 
            sslmode="require",
            connect_timeout=10
        )
    except Exception as e:
        st.error(f"❌ عذراً، نواجه مشكلة تقنية في الاتصال بالسيرفر. يرجى تحديث الصفحة. {e}")
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
    st.markdown("<h1 style='text-align: center; color: #38bdf8;'>مؤسسة نسق للدعاية والإعلان</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>بوابة الإدارة السحابية ☁️</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            serial = st.text_input("👤 الرقم الوظيفي")
            password = st.text_input("🔑 كلمة المرور", type="password")
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
                diff = current_count - st.session_state.last_order_count
                st.toast(f"🔔 تنبيه: تم إضافة {diff} طلب جديد في النظام!", icon="🚨")
                st.session_state.last_order_count = current_count
        except: pass

# --- واجهة المدير (Admin) ---
def admin_portal():
    with st.sidebar:
        st.markdown(f"### 👋 المدير: {st.session_state.emp_name}")
        menu = st.radio("القائمة الرئيسية:", [
            "📊 لوحة القيادة", 
            "➕ طلب تشغيل جديد", 
            "📦 إدارة الطلبات (الورشة)", 
            "🧾 سجل الفواتير",
            "💰 التقارير المالية",
            "👥 إدارة العملاء (CRM)",
            "💬 المديونيات والواتساب",
            "📢 التسويق وحملات التهاني",
            "🧮 حاسبة الأسعار والهدر",
            "👨‍🎨 إدارة المصممين",
            "👨‍💼 إدارة الموظفين",
            "⚙️ إعدادات الأقسام"
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
        st.markdown(f"### 👋 {st.session_state.emp_name}")
        st.markdown(f"**الرتبة:** {st.session_state.role}")
        st.divider()
        if st.button("🚪 تسجيل الخروج", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    if st.session_state.role == "Designer":
        render_designer(conn, st.session_state.emp_name)
    elif st.session_state.role == "Technician":
        render_technician(conn, st.session_state.emp_name)
    elif st.session_state.role == "Installer":
        render_installer(conn, st.session_state.emp_name)

# --- تشغيل التطبيق ---
if not st.session_state.logged_in:
    login_screen()
else:
    check_notifications()
    if st.session_state.role == "Admin":
        admin_portal()
    else:
        employee_portal()
