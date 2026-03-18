# web_ui/accounts.py
import streamlit as st
import pandas as pd
from datetime import datetime

def render_accounts(conn):
    st.markdown("""
        <div style="text-align: right;">
            <h1 style="color: #1e293b;">💰 التقارير المالية والأرباح</h1>
            <p style="color: #64748b;">ملخص مالي مباشر يوضح الأداء المالي للمؤسسة بناءً على كافة أوامر العمل المسجلة.</p>
        </div>
    """, unsafe_allow_html=True)

    try:
        conn.rollback()
        # جلب البيانات المالية
        query = "SELECT price, vat, total_with_vat, paid, cost, profit, status FROM orders"
        df = pd.read_sql(query, conn)

        if df.empty:
            st.warning("⚠️ لا توجد بيانات مالية مسجلة حتى الآن.")
            return

        # حسابات إجمالية
        total_revenue = df['price'].sum()
        total_paid = df['paid'].sum()
        total_debts = df['total_with_vat'].sum() - total_paid
        total_profit = df['profit'].sum()

        # عرض البطاقات المالية بتصميم واضح
        col1, col2, col3 = st.columns(3)
        col1.metric("إجمالي الدخل (بدون ضريبة)", f"{total_revenue:,.2f} ر.س", delta="قيمة العقود")
        col2.metric("مديونيات العملاء (مبالغ معلقة)", f"{total_debts:,.2f} ر.س", delta="تحت التحصيل", delta_color="inverse")
        col3.metric("صافي الربح المتوقع", f"{total_profit:,.2f} ر.س", delta="بعد خصم التكاليف")

        st.divider()

        # قسم تحليل الأرباح والإيرادات
        st.markdown("### 📊 تحليل الأرباح والإيرادات")
        
        # جدول تفصيلي
        st.dataframe(df, width="stretch", hide_index=True)

    except Exception as e:
        st.error(f"❌ حدث خطأ في تحميل البيانات المالية: {e}")
