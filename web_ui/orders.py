import streamlit as st
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components

def render_orders(conn):
    st.markdown("""
        <style>
        .main-title { text-align: right; color: #1e293b; font-size: 28px; font-weight: bold; border-right: 5px solid #fb923c; padding-right: 15px; }
        .order-card { background-color: #f8fafc; border: 1px solid #e2e8f0; padding: 15px; border-radius: 10px; margin-bottom: 15px; }
        </style>
        <h1 class="main-title">📦 إدارة العمليات والمستندات</h1>
    """, unsafe_allow_html=True)

    try:
        cursor = conn.cursor()
        
        # 1. جلب البيانات (استعلام آمن يستخدم الأسماء الصحيحة)
        # لاحظ أننا استبعدنا 'price' واستخدمنا 'unit_price' و 'total_price'
        query = """
            SELECT 
                id, work_order_sn, client_name, phone, project_name, 
                category, material_type, qty, unit_price, total_price, 
                paid_amount, remaining_amount, current_stage, status, details
            FROM orders 
            ORDER BY id DESC
        """
        df = pd.read_sql(query, conn)
        
        if df.empty:
            st.info("📭 لا توجد طلبات مسجلة حالياً.")
            return

        # 2. نظام البحث والتصفية
        search = st.text_input("🔍 ابحث برقم الطلب أو اسم العميل:")
        if search:
            df = df[df['client_name'].str.contains(search, case=False) | 
                    df['work_order_sn'].str.contains(search, case=False)]

        # 3. عرض الطلبات كبطاقات تفاعلية
        for index, row in df.iterrows():
            with st.container():
                st.markdown(f"""
                <div class="order-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: #64748b; font-size: 0.9em;">#{row['work_order_sn']}</span>
                        <span style="background: #fff7ed; color: #ea580c; padding: 2px 10px; border-radius: 15px; font-size: 0.8em;">{row['current_stage']}</span>
                    </div>
                    <h3 style="margin: 5px 0; color: #1e293b;">{row['client_name']}</h3>
                    <p style="margin: 0; font-size: 0.9em; color: #475569;"><b>المشروع:</b> {row['project_name']} | <b>القسم:</b> {row['category']}</p>
                    <p style="margin: 5px 0; font-size: 0.9em; color: #1e293b;">
                        💰 الإجمالي: {row['total_price']} | 
                        <span style="color: green;">المدفوع: {row['paid_amount']}</span> | 
                        <span style="color: red;">المتبقي: {row['remaining_amount']}</span>
                    </p>
                </div>
                """, unsafe_allow_html=True)

                # أزرار التحكم لكل طلب
                col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
                
                # تحديث المرحلة (Status Update)
                with col1:
                    stages = ["التصميم", "الإنتاج", "التركيب", "مكتمل"]
                    new_stage = st.selectbox("المرحلة:", stages, index=stages.index(row['current_stage']) if row['current_stage'] in stages else 0, key=f"stage_{row['id']}")
                    if st.button("تحديث", key=f"upd_{row['id']}"):
                        cursor.execute("UPDATE orders SET current_stage=%s WHERE id=%s", (new_stage, row['id']))
                        conn.commit()
                        st.rerun()

                # حذف الطلب
                with col2:
                    if st.button("🗑️ حذف", key=f"del_{row['id']}", type="secondary", use_container_width=True):
                        cursor.execute("DELETE FROM orders WHERE id=%s", (row['id'],))
                        conn.commit()
                        st.rerun()

                # واتساب
                with col3:
                    msg = f"مرحباً {row['client_name']}، طلبكم {row['work_order_sn']} الآن في مرحلة {row['current_stage']}. المتبقي: {row['remaining_amount']} ر.س"
                    wa_url = f"https://wa.me/{row['phone']}?text={msg}"
                    st.markdown(f"[💬 واتساب]({wa_url})")

                # طباعة (سيتم ربطها بملفات الـ HTML لاحقاً)
                with col4:
                    if st.button("🧾 فاتورة", key=f"prt_{row['id']}", use_container_width=True):
                        st.info("جاري تجهيز الطباعة...")

                st.markdown("<hr style='margin: 10px 0; opacity: 0.2;'>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ حدث خطأ في قاعدة البيانات: {e}")
        st.info("نصيحة: تأكد من أن أسماء الأعمدة في قاعدة البيانات تطابق الكود (unit_price, total_price, paid_amount).")
