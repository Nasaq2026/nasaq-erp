import streamlit as st
import sys
import os

# إضافة المسارات
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.db_manager import db
from utils.auth import auth
from web_ui import (
    dashboard, new_order, orders, designer, 
    technician, installer, accounts, marketing, nasaq_ai,
    settings, tracking_page  # استيراد الملفات الجديدة
)

st.set_page_config(page_title="نَسق ERP", layout="wide")

# --- منطق التتبع التلقائي للعميل (Query Params) ---
# إذا دخل العميل عبر رابط يحتوي على ?sn=xxxx
query_params = st.query_params
if "sn" in query_params:
    tracking_page.render_tracking(query_params["sn"])
    st.stop() # إيقاف بقية الكود لكي لا يظهر نظام الدخول للعميل

# --- نظام الجلسة والدخول المعتاد ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    # واجهة تسجيل الدخول (نفس الكود السابق)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.title("🎯 دخول نظام نَسق")
        u = st.text_input("المستخدم")
        p = st.text_input("كلمة المرور", type="password")
        if st.button("دخول"):
            user = auth.verify_login(u, p)
            if user:
                auth.create_user_session(user)
                st.rerun()
            else:
                st.error("بيانات خاطئة")
else:
    # --- القائمة الجانبية بعد الدخول ---
    with st.sidebar:
        st.write(f"مرحباً: {st.session_state.user_name}")
        menu = ["الرئيسية 📊", "طلب جديد ➕", "إدارة العمليات ⚙️", "تتبع الطلبات 🔍"]
        
        # إضافة خيار الإعدادات للآدمن فقط
        if st.session_state.user_role == "Admin":
            menu.append("إعدادات المؤسسة ⚙️")
            menu.append("Nasaq AI 🤖")
            
        choice = st.radio("القائمة", menu)
        if st.button("خروج"):
            auth.logout()

    # --- التوجيه (Routing) ---
    if choice == "الرئيسية 📊":
        dashboard.render_dashboard(db.get_connection())
    elif choice == "طلب جديد ➕":
        new_order.render_new_order(db.get_connection())
    elif choice == "إدارة العمليات ⚙️":
        orders.render_orders(db.get_connection())
    elif choice == "تتبع الطلبات 🔍":
        tracking_page.render_tracking()
    elif choice == "إعدادات المؤسسة ⚙️":
        settings.render_settings()
    elif choice == "Nasaq AI 🤖":
        nasaq_ai.render_ai(db.get_connection())
