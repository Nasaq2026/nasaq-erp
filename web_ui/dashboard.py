import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

def render_dashboard(conn):
    st.markdown("""
        <div style="text-align: right;">
            <h1 style="color: #1e293b;">📊 لوحة قيادة نَسق (Nasaq Dashboard)</h1>
            <p style="color: #64748b;">ملخص الأداء المالي والتشغيلي لمؤسسة موديول للدعاية والإعلان.</p>
        </div>
    """, unsafe_allow_html=True)

    try:
        cursor = conn.cursor()

        # 1. جلب البيانات الأساسية للعمليات
        cursor.execute("SELECT * FROM orders")
        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(cursor.fetchall(), columns=columns)

        if df.empty:
            st.info("📭 لا توجد بيانات كافية لعرض الإحصائيات حالياً.")
            return

        # 2. قسم المؤشرات الرئيسية (KPIs)
        st.markdown("### 📈 مؤشرات الأداء")
        total_orders = len(df)
        total_revenue = df['total_with_vat'].sum()
        # حساب الربح إذا كان العمود موجوداً، وإلا يتم حسابه يدوياً
        total_profit = df['profit'].sum() if 'profit' in df.columns else (df['price'].sum() - df['cost'].sum())
        active_orders = len(df[df['status'] == 'نشط'])

        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("إجمالي الطلبات", f"{total_orders}")
        kpi2.metric("إجمالي الإيرادات", f"{total_revenue:,.2f} ر.س")
        kpi3.metric("صافي الربح التقديري", f"{total_profit:,.2f} ر.س")
        kpi4.metric("طلبات قيد التنفيذ", f"{active_orders}")

        st.divider()

        # 3. التحليل البصري (Charts)
        col_charts_1, col_charts_2 = st.columns(2)

        with col_charts_1:
            st.markdown("#### 🛠️ توزيع الطلبات حسب المرحلة")
            stage_counts = df['current_stage'].value_counts().reset_index()
            fig_stage = px.pie(stage_counts, values='count', names='current_stage', 
                             hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_stage, use_container_width=True)

        with col_charts_2:
            st.markdown("#### 💰 الإيرادات حسب القسم")
            cat_revenue = df.groupby('category')['total_with_vat'].sum().reset_index()
            fig_cat = px.bar(cat_revenue, x='category', y='total_with_vat', 
                            color='category', text_auto='.2s')
            st.plotly_chart(fig_cat, use_container_width=True)

        st.divider()

        # 4. جدول آخر 5 طلبات (بلمسة جمالية)
        st.markdown("### 🕒 أحدث الطلبات المستلمة")
        latest_df = df.sort_values(by='id', ascending=False).head(5)
        # تصفية الأعمدة المهمة للمدير فقط
        display_cols = ['work_order_sn', 'client_name', 'category', 'total_with_vat', 'current_stage', 'status']
        st.table(latest_df[display_cols])

    except Exception as e:
        st.error(f"❌ حدث خطأ أثناء تحميل لوحة البيانات: {e}")

# استدعاء دالة التحذيرات في الملف الرئيسي (web_app.py) لإخفاء رسائل Pandas
