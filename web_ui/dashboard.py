import streamlit as st
import pandas as pd
import plotly.express as px
import os
import requests
from streamlit_lottie import st_lottie

# 🛠️ حل مشكلة مسار اللوجو (الخروج لمجلد nasaq-erp الرئيسي)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGO_PATH = os.path.join(BASE_DIR, "assets", "logo.png")

# دالة تحميل الأيقونات المتحركة بأمان
def load_lottieurl(url):
    try:
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else None
    except:
        return None

def render_dashboard(conn):
    # 1. تحميل الأيقونات (أرقام مالية وصندوق طلبات)
    lottie_money = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_y9m8vt7h.json")
    lottie_box = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_v74w96it.json")

    # 2. عرض اللوجو أو العنوان بأمان
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=150)
    else:
        st.markdown("<h1 style='color: #3b82f6;'>🎯 نَسق ERP</h1>", unsafe_allow_html=True)

    st.markdown("""
        <div style="text-align: right; margin-bottom: 20px;">
            <h2 style="color: #1e293b;">📊 لوحة قيادة موديول (الذكاء المالي)</h2>
            <p style="color: #64748b;">تحليل فوري للمبيعات، الأرباح، وأداء الفنيين.</p>
        </div>
    """, unsafe_allow_html=True)

    try:
        cursor = conn.cursor()
        # جلب البيانات يدوياً لتجنب تحذيرات Pandas
        cursor.execute("SELECT * FROM orders")
        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(cursor.fetchall(), columns=columns)

        if df.empty:
            st.info("📭 لا توجد بيانات مسجلة حالياً لعرضها.")
            return

        # 3. قسم الإحصائيات (KPIs) مع الأيقونات المتحركة
        col_m1, col_m2, col_m3 = st.columns([1, 1, 1])
        
        with col_m1:
            if lottie_money: st_lottie(lottie_money, height=100, key="money")
            total_rev = df['total_with_vat'].sum()
            st.metric("إجمالي الإيرادات", f"{total_rev:,.2f} ر.س")

        with col_m2:
            if lottie_box: st_lottie(lottie_box, height=100, key="box")
            active_count = len(df[df['status'] == 'نشط'])
            st.metric("طلبات قيد التنفيذ", active_count)

        with col_m3:
            # حساب الربح التقديري (السعر - التكلفة)
            total_profit = (df['price'].sum() - df['cost'].sum()) if 'cost' in df.columns else 0
            st.metric("صافي الربح التقديري", f"{total_profit:,.2f} ر.س", delta="نمو مستقر")

        st.divider()

        # 4. الرسوم البيانية التفاعلية
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown("#### 🔄 سير العمل (حسب المرحلة)")
            stage_fig = px.funnel(df.groupby('current_stage').size().reset_index(name='العدد'), 
                                 y='current_stage', x='العدد', color_discrete_sequence=['#3b82f6'])
            st.plotly_chart(stage_fig, use_container_width=True)

        with c2:
            st.markdown("#### 🥧 أرباح الأقسام (ليزر، كلادينج، مطبوعات)")
            cat_fig = px.pie(df, values='total_with_vat', names='category', hole=0.5,
                            color_discrete_sequence=px.colors.sequential.RdBu)
            st.plotly_chart(cat_fig, use_container_width=True)

        # 5. جدول المتابعة السريع
        st.markdown("### 📋 أحدث 5 عمليات")
        st.dataframe(df.sort_values('id', ascending=False).head(5)[['work_order_sn', 'client_name', 'total_with_vat', 'status']], 
                     use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"❌ حدث خطأ أثناء تحميل البيانات: {e}")
