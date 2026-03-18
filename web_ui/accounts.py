# web_ui/accounts.py
import streamlit as st
import pandas as pd

def render_accounts(conn):
    st.markdown("""
        <div style="text-align: right;">
            <h1 style="color: #1e293b;">🧾 الفواتير والتقارير المالية</h1>
            <p style="color: #64748b;">ملخص مالي مباشر يوضح الإيرادات، التكاليف، وصافي الأرباح.</p>
        </div>
    """, unsafe_allow_html=True)

    try:
        conn.rollback()
        # جلب البيانات المالية من جدول الطلبات
        query = "SELECT price, vat, total_with_vat, paid, cost, profit FROM orders"
        df = pd.read_sql(query, conn)

        if df.empty:
            st.warning("⚠️ لا توجد بيانات مالية مسجلة حتى الآن.")
            return

        # الحسابات الإجمالية
        total_rev = df['price'].sum()
        total_paid = df['paid'].sum()
        total_costs = df['cost'].sum()
        net_profit = df['profit'].sum()
        pending = df['total_with_vat'].sum() - total_paid

        # عرض البطاقات المالية
        c1, c2, c3 = st.columns(3)
        c1.metric("إجمالي العقود (بدون ضريبة)", f"{total_rev:,.2f} ر.س")
        c2.metric("المبالغ المحصلة", f"{total_paid:,.2f} ر.س", delta=f"المتبقي: {pending:,.2f}")
        c3.metric("صافي الربح المتوقع", f"{net_profit:,.2f} ر.س", delta=f"التكاليف: {total_costs:,.2f}", delta_color="inverse")

        st.divider()
        st.markdown("### 📊 تفاصيل السجل المالي")
        st.dataframe(df, width="stretch", hide_index=True)

    except Exception as e:
        st.error(f"❌ خطأ في تحميل البيانات المالية: {e}")
