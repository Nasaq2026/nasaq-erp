import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
from utils.invoice import generate_invoice_html 

def render_invoices(conn):
    st.markdown("""
        <div style="text-align: right;">
            <h1 style="color: #1e293b;">🧾 سجل الفواتير الضريبية</h1>
            <p style="color: #64748b;">نظام نَسق - عرض المبالغ والضريبة لعام 2026.</p>
        </div>
    """, unsafe_allow_html=True)

    try:
        conn.rollback()
        cursor = conn.cursor()

        # جلب البيانات المالية
        query = """
            SELECT 
                work_order_sn AS "رقم الفاتورة", client_name AS "العميل", 
                price AS "المبلغ", vat AS "الضريبة", total_with_vat AS "الإجمالي",
                paid AS "المدفوع", (total_with_vat - paid) AS "المتبقي", phone
            FROM orders ORDER BY id DESC
        """
        df = pd.read_sql(query, conn)

        if not df.empty:
            # التحديث الجديد: استخدام width='stretch' بدلاً من use_container_width
            st.dataframe(
                df.drop(columns=['phone']).style.format("{:,.2f} ر.س", subset=["المبلغ", "الضريبة", "الإجمالي", "المدفوع", "المتبقي"]),
                width='stretch', # التعديل المطلوب لعام 2026
                hide_index=True
            )

            st.divider()

            # اختيار الفاتورة للطباعة
            selected_inv = st.selectbox("🎯 اختر رقم الفاتورة لإصدار PDF:", df["رقم الفاتورة"].tolist())

            # تحديث الأزرار لتتوافق مع معايير 2026
            if st.button("📄 توليد الفاتورة الآن", width='stretch'): 
                cursor.execute("""
                    SELECT work_order_sn, client_name, phone, details, total_with_vat, paid, 
                    (total_with_vat - paid) as debt, category, material_type, dimensions, expected_delivery
                    FROM orders WHERE work_order_sn = %s
                """, (selected_inv,))
                row = cursor.fetchone()
                
                if row:
                    keys = ['work_order_sn', 'client_name', 'phone', 'details', 'total_with_vat', 'paid', 'debt', 'category', 'material_type', 'dimensions', 'expected_delivery']
                    order_dict = dict(zip(keys, row))
                    
                    cursor.execute("SELECT * FROM clients WHERE phone = %s", (str(order_dict['phone']),))
                    client_data = cursor.fetchone()
                    
                    html_inv = generate_invoice_html(order_dict, client_data)
                    
                    # معاينة وطباعة
                    components.html(f"{html_inv} <script>window.onload = function() {{ window.print(); }}</script>", height=800, scrolling=True)
                else:
                    st.error("البيانات غير موجودة في القاعدة.")
        else:
            st.warning("لا توجد فواتير.")

    except Exception as e:
        st.error(f"خطأ: {e}")
