import streamlit as st
import sys
import os

# إضافة المسارات لضمان عمل الاستيراد بشكل صحيح
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# استيراد المدير والأمان (النظام الجديد)
from utils.db_manager import db
from utils.auth import auth
from style_utils import apply_custom_design

# استيراد واجهات المستخدم
from web_ui import (
    dashboard, new_order, orders, designer, 
    technician, installer, accounts, marketing, nasaq_ai
)

# 1. إعدادات الصفحة والبراندينج
st.set_page_config(
    page_title="نَسق ERP | Moudesign",
    page_icon="🎯",
    layout="wide"
)

# تطبيق لمسة موديزاين البصرية
apply_custom_design()

# 2. إدارة حالة الجلسة (Session State)
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_role = None
    st.session_state.user_name = None

# --- واجهة تسجيل الدخول ---
if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        # يمكنك وضع شعارك هنا
        st.image("https://moudesign.com/logo.png", width=180) 
        st.markdown("<h2 style='text-align:center;'>نظام نَسق لإدارة المطبوعات</h2>", unsafe_allow_html=True)
        
        with st.container():
            username = st.text_input("اسم المستخدم")
            password = st.text_input("كلمة المرور", type="password")
            
            if st.button("دخول للنظام 🚀", use_container_width=True):
                user_data = auth.verify_login(username, password)
                if user_data:
                    auth.create_user_session(user_data)
                    st.success(f"مرحباً {user_data['emp_name']}، جاري تحضير لوحة التحكم...")
                    st.rerun()
                else:
                    st.error("❌ عذراً، اسم المستخدم أو كلمة المرور غير صحيحة.")

# --- الواجهة الرئيسية بعد الدخول الآمن ---
else:
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.user_name}")
        st.info(f"الرتبة: **{st.session_state.user_role}**")
        st.divider()
        
        # القائمة الديناميكية حسب الصلاحيات
        menu_options = ["الرئيسية 📊"]
        
        if st.session_state.user_role == "Admin":
            menu_options += ["طلب جديد ➕", "إدارة العمليات ⚙️", "الحسابات 💰", "التسويق 📢", "الموظفين 👥", "Nasaq AI 🤖"]
        elif st.session_state.user_role == "Designer":
            menu_options += ["مساحة التصميم 🎨"]
        elif st.session_state.user_role == "Technician":
            menu_options += ["قسم الإنتاج 🖨️"]
        elif st.session_state.user_role == "Installer":
            menu_options += ["الميدان 🏗️"]
            
        choice = st.radio("القائمة الرئيسية", menu_options)
        
        st.markdown("<br>" * 5, unsafe_allow_html=True)
        if st.button("تسجيل الخروج 🚪", use_container_width=True):
            auth.logout()

    # --- توجيه الصفحات (Routing Logic) ---
    if choice == "الرئيسية 📊":
        dashboard.render_dashboard(db.get_connection())
        
    elif choice == "طلب جديد ➕":
        new_order.render_new_order(db.get_connection())
        
    elif choice == "إدارة العمليات ⚙️":
        orders.render_orders(db.get_connection())
        
    elif choice == "مساحة التصميم 🎨":
        designer.render_designer(db.get_connection(), st.session_state.user_name)

    elif choice == "Nasaq AI 🤖":
        nasaq_ai.render_ai(db.get_connection())

    # يمكنك إكمال بقية الروابط هنا بنفس الطريقة...
