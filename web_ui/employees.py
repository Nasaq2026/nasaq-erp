# web_ui/employees.py
import streamlit as st
import pandas as pd

def render_employees(conn):
    st.markdown("""
        <div style="text-align: right;">
            <h1 style="color: #1e293b;">👨‍💼 إدارة الموظفين والصلاحيات</h1>
            <p style="color: #64748b;">مراجعة قائمة الموظفين المسجلين، أدوارهم الوظيفية، وبيانات الاتصال الخاصة بهم.</p>
        </div>
    """, unsafe_allow_html=True)

    try:
        conn.rollback()
        # جلب البيانات بتنسيق احترافي
        query = """
            SELECT 
                serial_number AS "الرقم الوظيفي", 
                emp_name AS "اسم الموظف", 
                role AS "الصلاحية", 
                phone AS "رقم الجوال" 
            FROM employees 
            ORDER BY id ASC
        """
        df = pd.read_sql(query, conn)
        
        if not df.empty:
            # ✅ تحديث العرض للكود الجديد width="stretch"
            st.dataframe(
                df, 
                width="stretch", 
                hide_index=True,
                column_config={
                    "الرقم الوظيفي": st.column_config.TextColumn("الرقم الوظيفي"),
                    "اسم الموظف": st.column_config.TextColumn("اسم الموظف"),
                    "الصلاحية": st.column_config.TextColumn("الصلاحية"),
                    "رقم الجوال": st.column_config.TextColumn("رقم الجوال")
                }
            )
        else:
            st.info("📭 لا يوجد موظفين مسجلين حالياً في النظام.")

    except Exception as e:
        st.error(f"❌ خطأ في تحميل بيانات الموظفين: {e}")
