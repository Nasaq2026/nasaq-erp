# web_ui/employees.py
import streamlit as st
import pandas as pd

def render_employees(conn):
    st.markdown("""
        <div style="text-align: right;">
            <h1 style="color: #1e293b;">👨‍💼 إدارة الموظفين والصلاحيات</h1>
            <p style="color: #64748b;">إضافة موظفين جدد، تحديد أدوارهم، ومتابعة القائمة الحالية.</p>
        </div>
    """, unsafe_allow_html=True)

    try:
        cursor = conn.cursor()
        conn.rollback()

        # --- 1. قسم إضافة موظف جديد ---
        with st.expander("➕ إضافة موظف جديد للنظام", expanded=False):
            with st.form("add_emp_form"):
                col1, col2 = st.columns(2)
                name = col1.text_input("اسم الموظف الكامل *")
                password = col2.text_input("كلمة مرور الدخول *", type="password")
                
                col3, col4 = st.columns(2)
                role = col3.selectbox("الصلاحية / الدور الوظيفي", ["Designer", "Technician", "Installer", "Admin"])
                phone = col4.text_input("رقم الجوال (اختياري)")
                
                submit_btn = st.form_submit_button("إعتماد الإضافة ✅", use_container_width=True)

                if submit_btn:
                    if name and password:
                        # توليد الرقم الوظيفي تلقائياً (نفس منطق الديسكتوب لضمان التوافق)
                        prefix = role[0].upper()
                        cursor.execute("SELECT COUNT(*) FROM employees WHERE role = %s", (role,))
                        count = cursor.fetchone()[0] + 1001
                        serial = f"{prefix}-{count}"

                        try:
                            cursor.execute("""
                                INSERT INTO employees (emp_name, serial_number, password, role, phone)
                                VALUES (%s, %s, %s, %s, %s)
                            """, (name, serial, password, role, phone))
                            conn.commit()
                            st.success(f"✅ تم تسجيل {name} بنجاح! الرقم الوظيفي المخصص: {serial}")
                            st.rerun()
                        except Exception as e:
                            conn.rollback()
                            st.error(f"⚠️ خطأ: قد يكون الاسم أو الرقم الوظيفي مسجل مسبقاً. التفاصيل: {e}")
                    else:
                        st.warning("⚠️ يرجى تعبئة الحقول الأساسية (الاسم وكلمة المرور)")

        st.divider()

        # --- 2. عرض قائمة الموظفين ---
        st.markdown("### 📋 قائمة الطاقم الحالي")
        query = """
            SELECT 
                serial_number AS "الرقم الوظيفي", 
                emp_name AS "اسم الموظف", 
                role AS "الصلاحية", 
                phone AS "رقم الجوال",
                id
            FROM employees 
            ORDER BY id ASC
        """
        df = pd.read_sql(query, conn)
        
        if not df.empty:
            # عرض الجدول بدون عمود الـ ID (لأنه للاستخدام البرمجي فقط)
            st.dataframe(
                df.drop(columns=["id"]), 
                use_container_width=True, 
                hide_index=True
            )
            
            # --- 3. قسم الحذف ---
            with st.expander("🗑️ منطقة الحذف (إدارة النظام)"):
                emp_to_del = st.selectbox("اختر موظفاً لإزالته نهائياً:", 
                                         options=df.index, 
                                         format_func=lambda x: f"{df.iloc[x]['الرقم الوظيفي']} - {df.iloc[x]['اسم الموظف']}")
                
                if st.button("تأكيد حذف الموظف ⚠️", type="secondary"):
                    target_id = int(df.iloc[emp_to_del]['id'])
                    cursor.execute("DELETE FROM employees WHERE id = %s", (target_id,))
                    conn.commit()
                    st.toast(f"تم حذف الموظف بنجاح")
                    st.rerun()
        else:
            st.info("📭 لا يوجد موظفين مسجلين حالياً في النظام.")

    except Exception as e:
        st.error(f"❌ خطأ في معالجة بيانات الموظفين: {e}")
