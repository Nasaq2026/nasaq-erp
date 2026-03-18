# web_ui/designers.py
import streamlit as st
import pandas as pd

def render_designers(conn):
    st.title("👨‍🎨 إدارة فريق التصميم (مرتبط بجدول الموظفين)")
    st.info("💡 هذه الشاشة تعرض فقط الموظفين الذين يملكون صلاحية 'Designer' في جدول الموظفين الرئيسي.")

    try:
        conn.rollback()
        cursor = conn.cursor()

        # 1. جلب المصممين فقط من جدول الموظفين الرئيسي
        query = """
            SELECT serial_number AS "الرقم الوظيفي", emp_name AS "اسم المصمم", phone AS "رقم الجوال"
            FROM employees 
            WHERE role = 'Designer'
            ORDER BY id ASC
        """
        df = pd.read_sql(query, conn)

        if not df.empty:
            st.markdown("### 📋 قائمة المصممين المعتمدين")
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            st.divider()
            
            # 2. عرض حجم العمل الحالي للمصممين الموجودين في الجدول
            st.markdown("### 📊 حجم العمل الحالي (الطلبات قيد التنفيذ)")
            query_perf = """
                SELECT 
                    designer AS "اسم المصمم", 
                    COUNT(*) AS "الطلبات قيد التنفيذ"
                FROM orders 
                WHERE current_stage = 'التصميم' AND status = 'نشط'
                GROUP BY designer
            """
            df_perf = pd.read_sql(query_perf, conn)

            if not df_perf.empty:
                st.bar_chart(data=df_perf, x="اسم المصمم", y="الطلبات قيد التنفيذ", color="#8B5CF6", use_container_width=True)
            else:
                st.success("✅ لا يوجد ضغط عمل حالياً على فريق التصميم.")
        else:
            st.warning("⚠️ لا يوجد موظفين بصلاحية 'Designer' في جدول الموظفين. يرجى إضافة مصمم أولاً من شاشة إدارة الموظفين.")

    except Exception as e:
        st.error(f"حدث خطأ أثناء ربط البيانات: {e}")