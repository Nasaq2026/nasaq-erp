# web_ui/invoices.py
import streamlit as st
import pandas as pd

def render_invoices(conn):
    st.title("🧾 سجل الفواتير الضريبية")
    st.info("عرض قائمة الفواتير الصادرة، المبالغ الضريبية، وحالة السداد.")

    try:
        conn.rollback()
        cursor = conn.cursor()

        # استعلام لجلب البيانات المالية الأساسية للفواتير
        query = """
            SELECT 
                work_order_sn AS "رقم الفاتورة", 
                client_name AS "العميل", 
                category AS "البيان",
                price AS "المبلغ (بدون ضريبة)", 
                vat AS "الضريبة (15%)", 
                total_with_vat AS "الإجمالي شامل الضريبة",
                paid AS "المبلغ المدفوع",
                (total_with_vat - paid) AS "المتبقي"
            FROM orders 
            ORDER BY id DESC
        """
        
        df = pd.read_sql(query, conn)

        if not df.empty:
            # تنسيق عرض الأرقام لتظهر كعملة (ر.س) بشكل احترافي
            st.dataframe(
                df.style.format({
                    "المبلغ (بدون ضريبة)": "{:,.2f} ر.س",
                    "الضريبة (15%)": "{:,.2f} ر.س",
                    "الإجمالي شامل الضريبة": "{:,.2f} ر.س",
                    "المبلغ المدفوع": "{:,.2f} ر.س",
                    "المتبقي": "{:,.2f} ر.س"
                }),
                use_container_width=True,
                hide_index=True
            )

            # إحصائيات سريعة في الأسفل
            st.divider()
            c1, c2, c3 = st.columns(3)
            total_vat = df["الضريبة (15%)"].sum()
            total_collected = df["المبلغ المدفوع"].sum()
            
            c1.metric("إجمالي ضريبة القيمة المضافة", f"{total_vat:,.2f} ر.س")
            c2.metric("إجمالي التحصيل النقدي", f"{total_collected:,.2f} ر.س")
            c3.info("💡 يمكنك تصدير هذا الجدول من زر التحميل في أعلى يمين الجدول عند الوقوف عليه بالماوس.")

        else:
            st.warning("لا توجد فواتير مسجلة حالياً في النظام.")

    except Exception as e:
        st.error(f"حدث خطأ أثناء تحميل سجل الفواتير: {e}")