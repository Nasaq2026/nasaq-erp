# web_ui/employees.py
import streamlit as st
import pandas as pd

def render_employees(conn):
    st.title("👨‍💼 إدارة الموظفين والصلاحيات")
    try:
        conn.rollback()
        query = """
            SELECT 
                serial_number AS "الرقم الوظيفي", 
                emp_name AS "اسم الموظف", 
                role AS "الصلاحية", 
                phone AS "رقم الجوال" 
            FROM employees ORDER BY id ASC
        """
        df = pd.read_sql(query, conn)
        st.dataframe(df, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"خطأ في تحميل الموظفين: {e}")