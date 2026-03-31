import streamlit as st
import pandas as pd

import streamlit as st
import urllib.parse

def render_collection_center(conn):
    st.subheader("💳 مركز التحصيل والمتابعة")
    
    # جلب العملاء الذين عليهم مبالغ متبقية
    query = "SELECT work_order_sn, client_name, phone, (total_with_vat - paid) as debt FROM orders WHERE (total_with_vat - paid) > 0"
    cursor = conn.cursor()
    cursor.execute(query)
    debtors = cursor.fetchall()

    for order_sn, name, phone, debt in debtors:
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.write(f"👤 **{name}** (طلب: {order_sn})")
        with col2:
            st.error(f"المتبقي: {debt:,.2f} ر.س")
        with col3:
            # رسالة واتساب احترافية
            msg = f"تحية طيبة من مؤسسة موديول ✨\nنود تذكيركم بالمبلغ المتبقي: {debt} ر.س\nرقم الطلب: {order_sn}\nشاكرين تعاونكم."
            link = f"https://wa.me/{phone}?text={urllib.parse.quote(msg)}"
            st.markdown(f"[📲 إرسال مطالبة]({link})")

def render_finance(conn):
    st.title("💰 الإدارة المالية والتحصيل")
    
    # دالة حقيقية لحساب المبالغ
    query = """
        SELECT work_order_sn, client_name, phone, total_with_vat, paid, 
        (total_with_vat - paid) as remaining 
        FROM orders WHERE (total_with_vat - paid) > 0
    """
    df_debts = pd.read_sql(query, conn)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("إجمالي المبالغ المستحقة", f"{df_debts['remaining'].sum():,.2f} ر.س", delta_color="inverse")
    
    st.subheader("⚠️ عملاء متأخرون عن السداد")
    for index, row in df_debts.iterrows():
        with st.container():
            c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
            c1.write(f"👤 {row['client_name']}")
            c2.write(f"🔴 المتبقي: {row['remaining']} ر.س")
            
            # زر إرسال مطالبة واتساب
            msg = f"عزيزنا {row['client_name']}، نذكركم بالمبلغ المتبقي لطلبكم {row['work_order_sn']} وقدره {row['remaining']} ر.س."
            link = f"https://wa.me/{row['phone']}?text={msg}"
            c3.markdown(f"[📩 مطالبة واتساب]({link})")
            
            if c4.button("📄 إصدار كشف", key=f"inv_{row['work_order_sn']}"):
                st.info("جاري تصدير PDF احترافي...")
