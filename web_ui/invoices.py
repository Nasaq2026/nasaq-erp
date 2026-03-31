import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
from utils.invoice import generate_invoice_html # استيراد دالة التصميم

def render_invoices(conn):
    st.markdown("""
        <div style="text-align: right;">
            <h1 style="color: #1e293b;">🧾 سجل الفواتير الضريبية</h1>
            <p style="color: #64748b;">عرض قائمة الفواتير الصادرة لـ "موديول"، المبالغ الضريبية، وحالة السداد.</p>
        </div>
    """, unsafe_allow_html=True)

    try:
        conn.rollback()
        cursor = conn.cursor()

        # 1. استعلام لجلب البيانات المالية الأساسية للفواتير
        query = """
            SELECT 
                work_order_sn AS "رقم الفاتورة", 
                client_name AS "العميل", 
                category AS "البيان",
                price AS "المبلغ (بدون ضريبة)", 
                vat AS "الضريبة (15%)", 
                total_with_vat AS "الإجمالي شامل الضريبة",
                paid AS "المبلغ المدفوع",
                (total_with_vat - paid) AS "المتبقي",
                phone
            FROM orders 
            ORDER BY id DESC
        """
        
        df = pd.read_sql(query, conn)

        if not df.empty:
            # عرض الجدول المالي
            st.dataframe(
                df.drop(columns=['phone']).style.format({
                    "المبلغ (بدون ضريبة)": "{:,.2f} ر.س",
                    "الضريبة (15%)": "{:,.2f} ر.س",
                    "الإجمالي شامل الضريبة": "{:,.2f} ر.س",
                    "المبلغ المدفوع": "{:,.2f} ر.س",
                    "المتبقي": "{:,.2f} ر.س"
                }),
                use_container_width=True,
                hide_index=True
            )

            st.divider()

            # --- قسم طباعة فاتورة محددة ---
            st.markdown("### 🖨️ إصدار فاتورة PDF")
            invoice_list = df["رقم الفاتورة"].tolist()
            selected_inv = st.selectbox("اختر رقم الفاتورة للطباعة:", invoice_list)

            if st.button("📄 توليد الفاتورة للطباعة", use_container_width=True):
                # جلب بيانات العميل والطلب بدقة للطباعة
                cursor.execute("""
                    SELECT work_order_sn, client_name, phone, details, total_with_vat, paid, 
                    (total_with_vat - paid) as debt, category, material_type, dimensions, expected_delivery
                    FROM orders WHERE work_order_sn = %s
                """, (selected_inv,))
                row = cursor.fetchone()
                
                if row:
                    # تحويل البيانات لقاموس للدالة
                    keys = ['work_order_sn', 'client_name', 'phone', 'details', 'total_with_vat', 'paid', 'debt', 'category', 'material_type', 'dimensions', 'expected_delivery']
                    order_dict = dict(zip(keys, row))
                    
                    # جلب بيانات العميل للـ QR
                    cursor.execute("SELECT * FROM clients WHERE phone = %s", (str(order_dict['phone']),))
                    client_data = cursor.fetchone()
                    
                    # إنشاء HTML الفاتورة
                    html_inv = generate_invoice_html(order_dict, client_data)
                    
                    # إضافة زر طباعة المتصفح وعرض الفاتورة
                    st.download_button("📥 تحميل ملف الفاتورة", data=html_inv, file_name=f"INV_{selected_inv}.html", mime="text/html")
                    components.html(f"{html_inv} <script>window.onload = function() {{ window.print(); }}</script>", height=800, scrolling=True)

            # إحصائيات سريعة في الأسفل
            st.divider()
            c1, c2 = st.columns(2)
            total_vat = df["الضريبة (15%)"].sum()
            total_collected = df["المبلغ المدفوع"].sum()
            
            c1.metric("إجمالي ضريبة القيمة المضافة", f"{total_vat:,.2f} ر.س")
            c2.metric("إجمالي التحصيل النقدي", f"{total_collected:,.2f} ر.س")

        else:
            st.warning("لا توجد فواتير مسجلة حالياً في النظام.")

    except Exception as e:
        st.error(f"حدث خطأ أثناء تحميل سجل الفواتير: {e}")
