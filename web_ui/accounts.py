# web_ui/accounts.py
import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
from utils.invoice import generate_invoice_html # 👈 استيراد الاسم الصحيح

def render_accounts(conn):
    st.markdown("<h1 style='text-align: right;'>🧾 الإدارة المالية والفواتير</h1>", unsafe_allow_html=True)

    try:
        conn.rollback()
        cursor = conn.cursor()

        # جلب الطلبات
        df = pd.read_sql("SELECT id, work_order_sn, client_name, phone, total_with_vat, paid FROM orders ORDER BY id DESC", conn)

        if df.empty:
            st.info("📭 لا توجد بيانات مالية حالياً.")
            return

        # اختيار الطلب لإصدار فاتورته
        st.markdown("### 📄 إصدار فاتورة ضريبية")
        order_to_bill = st.selectbox("اختر العميل/الطلب:", df['client_name'] + " - #" + df['id'].astype(str))
        selected_id = int(order_to_bill.split("#")[-1])

        if st.button("📝 توليد ومعاينة الفاتورة", width="stretch"):
            # جلب بيانات الطلب والعميل
            cursor.execute("SELECT * FROM orders WHERE id = %s", (selected_id,))
            order_row = cursor.fetchone()
            
            cursor.execute("SELECT * FROM clients WHERE phone = %s", (order_row[3],))
            client_row = cursor.fetchone()

            # توليد الكود
            invoice_data = generate_invoice_html(order_row, client_row)

            if invoice_data:
                st.success("✅ تم تجهيز الفاتورة!")
                
                # 1. معاينة حية (للتأكد أنها ليست فاضية)
                with st.expander("👁️ عرض معاينة الفاتورة", expanded=True):
                    components.html(invoice_data, height=500, scrolling=True)

                # 2. زر التحميل الفعلي (الحل النهائي)
                st.download_button(
                    label="📥 تحميل وحفظ الفاتورة (جاهزة للطباعة)",
                    data=invoice_data,
                    file_name=f"Invoice_{order_row[1]}.html",
                    mime="text/html",
                    width="stretch"
                )
            else:
                st.error("❌ فشل توليد بيانات الفاتورة، راجع مدخلات الطلب.")

    except Exception as e:
        st.error(f"❌ خطأ في النظام المالي: {e}")
