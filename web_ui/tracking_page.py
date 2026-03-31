import streamlit as st
from utils.db_manager import db

def render_tracking(order_sn=None):
    # تنسيق الصفحة لتناسب الجوال (Mobile First)
    st.markdown("""
        <style>
            .stApp { background-color: #f4f7f6; }
            .status-card { background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; }
            .step-active { color: #2ecc71; font-weight: bold; }
            .step-inactive { color: #bdc3c7; }
        </style>
    """, unsafe_allow_html=True)

    if not order_sn:
        st.title("🔍 تتبع طلبك")
        order_sn = st.text_input("أدخل رقم الطلب (SN):", placeholder="مثال: 2026-1001")

    if order_sn:
        order = db.execute_query("SELECT * FROM orders WHERE sn = %s", (order_sn,), fetch=True)
        
        if order:
            data = order[0]
            st.markdown(f"<div class='status-card'>", unsafe_allow_html=True)
            st.header(f"مرحباً {data['client_name']} 👋")
            st.subheader(f"حالة الطلب: {data['status']}")
            
            # راسم تقدم ذكي (Progress Bar)
            status_map = {"قيد الانتظار": 20, "في التصميم": 40, "تحت التنفيذ": 60, "جاهز للاستلام": 100}
            progress = status_map.get(data['status'], 10)
            st.progress(progress / 100)
            
            col1, col2 = st.columns(2)
            col1.metric("رقم الطلب", data['sn'])
            col2.metric("المبلغ المتبقي", f"{float(data['total'])-float(data['paid'])} ر.س")
            
            st.markdown("</div>", unsafe_allow_html=True)
            st.balloons() if data['status'] == "جاهز للاستلام" else None
        else:
            st.error("❌ عذراً، لم يتم العثور على هذا الرقم. تأكد من صحة الرقم الموجود في الفاتورة.")
