import streamlit as st
import sys
import os

# إضافة المسار الحالي لضمان رؤية المجلدات
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.db_manager import db
from utils.auth import auth
from web_ui import (
    dashboard, new_order, orders, tracking_page, nasaq_ai, settings
)

st.set_page_config(page_title="نَسق ERP - مؤسسة موديول", layout="wide", page_icon="🎯")

# --- منطق التتبع التلقائي للعميل (بدون تسجيل دخول) ---
query_params = st.query_params
if "sn" in query_params:
    tracking_page.render_tracking(query_params["sn"])
    st.stop() 

# --- نظام الجلسة والدخول ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.title("🎯 دخول نظام نَسق")
        u = st.text_input("اسم المستخدم")
        p = st.text_input("كلمة المرور", type="password")
        if st.button("تسجيل الدخول", use_container_width=True):
            user = auth.verify_login(u, p)
            if user:
                auth.create_user_session(user)
                st.rerun()
            else:
                st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة")
else:
    # --- القائمة الجانبية ---
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.user_name}")
        st.caption(f"الرتبة: {st.session_state.user_role}")
        st.divider()
        
        menu = ["الرئيسية 📊", "طلب جديد ➕", "إدارة العمليات ⚙️", "تتبع الطلبات 🔍"]
        
        if st.session_state.user_role == "Admin":
            menu.append("Nasaq AI 🤖")
            menu.append("إعدادات المؤسسة ⚙️")
            
        choice = st.radio("انتقل إلى:", menu)
        
        st.divider()
        if st.button("🚪 تسجيل الخروج", use_container_width=True):
            auth.logout()

    # --- التوجيه (Routing) ---
    conn = db.get_connection()
    
    if choice == "الرئيسية 📊":
        dashboard.render_dashboard(conn)
    elif choice == "طلب جديد ➕":
        new_order.render_new_order(conn)
    elif choice == "إدارة العمليات ⚙️":
        orders.render_orders(conn)
    elif choice == "تتبع الطلبات 🔍":
        tracking_page.render_tracking()
    elif choice == "Nasaq AI 🤖":
        nasaq_ai.render_ai(conn)
    elif choice == "إعدادات المؤسسة ⚙️":
        settings.render_settings()
