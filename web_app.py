import streamlit as st
import psycopg2
from web_ui import (
    dashboard, employees, categories, new_order, orders, 
    designer, technician, installer, accounts, debts, 
    invoices, marketing, nasaq_ai
)

# إعدادات الصفحة
st.set_page_config(page_title="نَسق ERP | Moudesign", layout="wide", initial_sidebar_state="expanded")

# الاتصال بقاعدة البيانات (يتم جلب البيانات من st.secrets في السيرفر)
def get_connection():
    return psycopg2.connect(st.secrets["postgres_url"])

conn = get_connection()

# نظام تسجيل الدخول وحفظ الجلسة
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 تسجيل الدخول - نظام نَسق")
    user = st.text_input("اسم المستخدم")
    pw = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        # هنا يتم التحقق من جدول employees
        cursor = conn.cursor()
        cursor.execute("SELECT emp_name, role FROM employees WHERE emp_name=%s AND password=%s", (user, pw))
        res = cursor.fetchone()
        if res:
            st.session_state.authenticated = True
            st.session_state.user_name = res[0]
            st.session_state.role = res[1]
            st.rerun()
        else:
            st.error("خطأ في البيانات")
else:
    # القائمة الجانبية الذكية بناءً على الصلاحيات
    with st.sidebar:
        st.image("logo.png", width=150) # شعار موديزاين
        st.write(f"👤 مرحباً: **{st.session_state.user_name}**")
        menu = ["الرئيسية"]
        
        if st.session_state.role == "Admin":
            menu += ["إضافة طلب", "إدارة العمليات", "الحسابات", "الفواتير", "المديونيات", "التسويق", "الموظفين", "الأقسام", "Nasaq AI"]
        elif st.session_state.role == "Designer":
            menu += ["مساحة التصميم"]
        elif st.session_state.role == "Technician":
            menu += ["قسم الإنتاج"]
        elif st.session_state.role == "Installer":
            menu += ["منصة الميدان"]
            
        choice = st.radio("القائمة الرئيسية", menu)

    # توجيه المستخدم للملف المناسب
    if choice == "الرئيسية": dashboard.render_dashboard(conn)
    elif choice == "إضافة طلب": new_order.render_new_order(conn)
    elif choice == "إدارة العمليات": orders.render_orders(conn)
    elif choice == "مساحة التصميم": designer.render_designer(conn, st.session_state.user_name)
    # ... وهكذا لبقية الملفات
