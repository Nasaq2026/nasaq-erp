# web_ui/accounts.py
import streamlit as st
import pandas as pd

def render_accounts(conn):
    st.title("💰 التقارير المالية والأرباح")
    st.info("💡 ملخص مالي مباشر يوضح الأداء المالي للمؤسسة بناءً على كافة أوامر العمل المسجلة.")

    try:
        conn.rollback()
        cursor = conn.cursor()

        # 1. جلب البيانات المالية الإجمالية
        cursor.execute("""
            SELECT 
                COALESCE(SUM(price), 0), 
                COALESCE(SUM(total_with_vat - paid), 0), 
                COALESCE(SUM(profit), 0),
                COALESCE(SUM(paid), 0)
            FROM orders
        """)
        income, debts, profit, actual_cash = cursor.fetchone()

        # 2. عرض البطاقات المالية بتصميم الويب المتجاوب
        col1, col2, col3 = st.columns(3)
        
        # إجمالي الدخل (قبل الضريبة)
        col1.metric("إجمالي الدخل (بدون ضريبة)", f"{income:,.2f} ر.س", delta="قيمة العقود")
        
        # مديونيات العملاء (باللون الأحمر للتنبيه)
        col2.metric("مديونيات العملاء (مبالغ معلقة)", f"{debts:,.2f} ر.س", delta="تحت التحصيل", delta_color="inverse")
        
        # صافي الربح (المبلغ الأهم للمدير)
        col3.metric("صافي الربح المتوقع", f"{profit:,.2f} ر.س", delta="بعد خصم التكاليف")

        st.divider()

        # 3. تحليل مالي مرئي (Visual Analytics)
        st.markdown("### 📊 تحليل الأرباح والإيرادات")
        
        # إنشاء جدول بيانات بسيط للرسم البياني
        chart_data = pd.DataFrame({
            "التصنيف": ["إجمالي الدخل", "صافي الربح", "النقد المحصل فعلياً"],
            "المبلغ (ر.س)": [income, profit, actual_cash]
        })
        
        col_chart, col_details = st.columns([2, 1])
        
        with col_chart:
            st.bar_chart(data=chart_data, x="التصنيف", y="المبلغ (ر.س)", color="#10B981", use_container_width=True)
            
        with col_details:
            st.markdown("#### 📝 ملاحظات سريعة:")
            st.write(f"- نسبة الربح من المبيعات: **{(profit/income*100) if income > 0 else 0:.1f}%**")
            st.write(f"- الكاش المحصل حالياً: **{actual_cash:,.2f} ر.س**")
            if debts > (income * 0.3):
                st.warning("⚠️ تنبيه: نسبة الديون مرتفعة (تتجاوز 30% من المبيعات).")

        st.divider()

        # 4. جدول تفصيلي للتدقيق (Audit Trail)
        st.markdown("### 🔍 تفاصيل الأرباح لكل طلب عمل")
        query_details = """
            SELECT 
                work_order_sn AS "أمر العمل", 
                client_name AS "العميل", 
                price AS "المبلغ", 
                cost AS "التكلفة", 
                profit AS "الربح"
            FROM orders 
            ORDER BY id DESC
        """
        df_details = pd.read_sql(query_details, conn)
        st.dataframe(df_details, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"حدث خطأ أثناء تحميل التقارير المالية: {e}")