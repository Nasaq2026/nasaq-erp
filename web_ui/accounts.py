# web_ui/accounts.py
import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
from utils.invoice import generate_invoice_html # استدعاء الدالة المطورة

def render_accounts(conn):
    st.markdown("""
        <div style="text-align: right;">
            <h1 style="color: #1e293b;">🧾 الإدارة المالية والفواتير</h1>
            <p style="color: #64748b;">استعراض الفواتير، التحصيل، وإصدار الفواتير الضريبية المعتمدة.</p>
        </div>
    """, unsafe_allow_html=True)

    try:
        conn.rollback()
        cursor = conn.cursor()

        # 1. جلب قائمة الطلبات لعرضها في جدول
        query = """
            SELECT id, work_order_sn, client_name, phone, expected_delivery, 
                   current_stage, price, vat, total_with_vat, paid, status, category
            FROM orders ORDER BY id DESC
        """
        df = pd.read_sql(query, conn)

        if df.empty:
            st.info("📭 لا توجد طلبات أو فواتير مسجلة حالياً.")
            return

        # 2. عرض ملخص مالي سريع (اختياري)
        col_m1, col_m2 = st.columns(2)
        total_all = df['total_with_vat'].sum()
        total_paid = df['paid'].sum()
        col_m1.metric("إجمالي المبيعات (شامل الضريبة)", f"{total_all:,.2f} ر.س")
        col_m2.metric("المبالغ المحصلة", f"{total_paid:,.2f} ر.س", delta=f"المتبقي: {total_all - total_paid:,.2f}")

        st.divider()

        # 3. اختيار الفاتورة المراد إصدارها
        st.markdown("### 📄 إصدار فاتورة عميل")
        order_options = {f"امر #{row['id']} - {row['client_name']}": row['id'] for _, row in df.iterrows()}
        selected_label = st.selectbox("اختر الطلب لإصدار الفاتورة:", list(order_options.keys()))
        order_id = order_options[selected_label]

        if st.button("📝 توليد ومعاينة الفاتورة الضريبية", width="stretch"):
            # جلب بيانات الطلب المختارة بالكامل
            cursor.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
            order_row = cursor.fetchone()
            
            # جلب بيانات العميل الضريبية (من جدول العملاء بناءً على رقم الجوال)
            cursor.execute("SELECT * FROM clients WHERE phone = %s", (order_row[3],))
            client_row = cursor.fetchone()

            if order_row:
                # توليد الـ HTML باستخدام الدالة اللي أصلحناها
                invoice_data = generate_invoice_html(order_row, client_row)
                
                if invoice_data and len(invoice_data) > 500: # تأكد أن الملف مش فاضي
                    st.success("✅ تم توليد الفاتورة بنجاح!")
                    
                    # --- 👁️ المعاينة الحية ---
                    st.markdown("---")
                    st.markdown("#### 👁️ معاينة الفاتورة")
                    components.html(invoice_data, height=600, scrolling=True)
                    
                    # --- 📥 زر التحميل النهائي ---
                    st.download_button(
                        label="📥 تحميل الفاتورة (جاهزة للطباعة PDF/HTML)",
                        data=invoice_data,
                        file_name=f"Nasaq_Invoice_{order_row[1]}.html",
                        mime="text/html",
                        width="stretch"
                    )
                else:
                    st.error("❌ حدث خطأ أثناء بناء ملف الفاتورة. تأكد من اكتمال بيانات الطلب.")

    except Exception as e:
        st.error(f"❌ خطأ تقني في جلب البيانات المالية: {e}")
