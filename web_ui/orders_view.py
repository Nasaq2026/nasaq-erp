import streamlit as st
import pandas as pd
from datetime import datetime

def render_new_order(conn):
    st.markdown("""
        <style>
        .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #1e293b; color: white; }
        .category-card { padding: 20px; border-radius: 15px; border: 1px solid #e2e8f0; text-align: center; transition: 0.3s; }
        .category-card:hover { border-color: #fb923c; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
        </style>
    """, unsafe_allow_html=True)

    st.title("✨ إنشاء طلب إعلاني جديد")
    
    # نظام المراحل (Wizard)
    if 'order_step' not in st.session_state:
        st.session_state.order_step = 1

    # شريط التقدم
    step_cols = st.columns(3)
    steps = ["👤 العميل", "📦 المنتج", "💰 المالية"]
    for i, s in enumerate(steps):
        color = "#fb923c" if st.session_state.order_step == i+1 else "#94a3b8"
        step_cols[i].markdown(f"<p style='text-align:center; color:{color}; font-weight:bold;'>{s}</p>", unsafe_allow_html=True)

    st.divider()

    # --- المرحلة 1: اختيار العميل ---
    if st.session_state.order_step == 1:
        st.subheader("1️⃣ بيانات العميل")
        col1, col2 = st.columns(2)
        
        cursor = conn.cursor()
        cursor.execute("SELECT client_name, phone FROM clients")
        clients = cursor.fetchall()
        client_names = [c[0] for c in clients]
        
        selected_client = col1.selectbox("اختر عميل مسجل:", ["-- جديد --"] + client_names)
        
        if selected_client == "-- جديد --":
            new_client_name = col1.text_input("اسم العميل الجديد:")
            new_client_phone = col2.text_input("رقم الجوال (للواتساب):")
        else:
            # جلب الجوال تلقائياً
            phone = [c[1] for c in clients if c[0] == selected_client][0]
            col2.info(f"رقم الجوال المرتبط: {phone}")

        if st.button("التالي: اختيار نوع المنتج ➡️"):
            st.session_state.order_step = 2
            st.rerun()

    # --- المرحلة 2: اختيار المنتج (التخصص الإعلاني) ---
    elif st.session_state.order_step == 2:
        st.subheader("2️⃣ تخصص المنتج والخامات")
        
        # توزيع المنتجات في بطاقات
        categories = {
            "حروف مضيئة": "💡",
            "أكريليك وفوركس": "🧩",
            "استكرات وبنرات": "🖼️",
            "هدايا ودروع": "🏆",
            "مطبوعات ورقية": "📄",
            "تجهيز مناسبات": "🎊"
        }
        
        cols = st.columns(3)
        for i, (name, icon) in enumerate(categories.items()):
            with cols[i % 3]:
                if st.button(f"{icon} \n {name}"):
                    st.session_state.selected_cat = name
                    st.session_state.order_step = 3
                    st.rerun()
        
        if st.button("⬅️ الرجوع"):
            st.session_state.order_step = 1
            st.rerun()
