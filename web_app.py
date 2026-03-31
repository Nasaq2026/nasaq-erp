import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor
import hashlib

# استيراد واجهات النظام (تأكد أن الملفات في مجلد web_ui)
from web_ui import (
    dashboard, new_order, orders, designer, 
    technician, installer, accounts, marketing, nasaq_ai
)
# استيراد أدوات التصميم والتعليقات التي صممناها
from style_utils import apply_custom_design, render_comment_section

# 1. إعدادات الصفحة الأساسية
st.set_page_config(
    page_title="نَسق ERP | Moudesign",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تطبيق التنسيق البصري الاحترافي
apply_custom_design()

# 2. الاتصال بقاعدة البيانات
def get_connection():
    try:
        return psycopg2.connect(st.secrets["postgres_url"])
    except:
        st.error("❌ فشل الاتصال بقاعدة البيانات. تحقق من الإعدادات.")
        return None

conn = get_connection()

# 3. إدارة الجلسة (Login System)
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_role = None
    st.session_state.user_name = None

# --- واجهة تسجيل الدخول ---
if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("https://moudesign.com/logo.png", width=200) # ضع رابط شعارك هنا
        st.markdown("<h2 style='text-align:center;'>دخول موظفي نَسق</h2>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            user = st.text_input("اسم المستخدم", placeholder="ادخل اسمك المسجل")
            password = st.text_input("كلمة المرور", type="password")
            submit = st.form_submit_button("دخول للنظام 🚀")
            
            if submit:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                cursor.execute("SELECT * FROM employees WHERE emp_name=%s AND password=%s", (user, password))
                employee = cursor.fetchone()
                
                if employee:
                    st.session_state.authenticated = True
                    st.session_state.user_role = employee['role']
                    st.session_state.user_name = employee['emp_name']
                    st.success("تم تسجيل الدخول بنجاح!")
                    st.rerun()
                else:
                    st.error("بيانات الدخول غير صحيحة")

# --- الواجهة الرئيسية بعد الدخول ---
else:
    # القائمة الجانبية (Sidebar)
    with st.sidebar:
        st.markdown(f"### مرحباً {st.session_state.user_name} 👋")
        st.write(f"🏷️ الصلاحية: `{st.session_state.user_role}`")
        st.divider()
        
        # توزيع القوائم حسب الرتبة
        if st.session_state.user_role == "Admin":
            menu = ["الرئيسية 📊", "طلب جديد ➕", "إدارة العمليات ⚙️", "الحسابات والفواتير 💰", "التسويق والعملاء 📢", "الذكاء الاصطناعي 🤖"]
        elif st.session_state.user_role == "Designer":
            menu = ["مساحة التصميم 🎨", "الطلبات النشطة"]
        elif st.session_state.user_role == "Technician":
            menu = ["قسم الإنتاج 🖨️"]
        elif st.session_state.user_role == "Installer":
            menu = ["منصة الميدان 🏗️"]
            
        choice = st.radio("انتقل إلى:", menu)
        
        st.spacer(10)
        if st.button("تسجيل الخروج 🚪"):
            st.session_state.authenticated = False
            st.rerun()

    # 4. توجيه الصفحات (Routing)
    if choice == "الرئيسية 📊":
        dashboard.render_dashboard(conn)
        
    elif choice == "طلب جديد ➕":
        new_order.render_new_order(conn)
        
    elif choice == "إدارة العمليات ⚙️":
        selected_sn = orders.render_orders(conn) # تأكد أن render_orders تعيد رقم الطلب المختار
        if selected_sn:
            render_comment_section(conn, selected_sn, st.session_state.user_name)
            
    elif choice == "مساحة التصميم 🎨":
        designer.render_designer(conn, st.session_state.user_name)
        
    elif choice == "قسم الإنتاج 🖨️":
        technician.render_technician(conn, st.session_state.user_name)
        
    elif choice == "منصة الميدان 🏗️":
        installer.render_installer(conn, st.session_state.user_name)

    elif choice == "الحسابات والفواتير 💰":
        tab1, tab2 = st.tabs(["السجل المالي", "الفواتير الضريبية"])
        with tab1: accounts.render_accounts(conn)
        with tab2: st.info("واجهة الفواتير قيد العرض...")

    elif choice == "الذكاء الاصطناعي 🤖":
        nasaq_ai.render_ai(conn)

# --- نظام التتبع العام (خارج تسجيل الدخول) ---
# إذا دخل العميل عبر رابط يحتوي على ?track=WO-1234
query_params = st.query_params
if "track" in query_params:
    st.divider()
    from web_ui import tracking_page
    tracking_page.render_tracking(conn, query_params["track"])
