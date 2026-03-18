# web_ui/technician.py
import streamlit as st
import pandas as pd

def render_technician(conn, emp_name):
    st.title("🖨️ قسم الإنتاج والطباعة")
    st.info("الطلبات الجاهزة للطباعة والتنفيذ:")
    
    try:
        conn.rollback()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, work_order_sn, client_name, dimensions, file_url, requires_install 
            FROM orders 
            WHERE current_stage = 'الطباعة والإنتاج' AND status = 'نشط' AND technician = %s
        """, (emp_name,))
        tasks = cursor.fetchall()
        
        if not tasks:
            st.success("🎉 لا توجد مهام إنتاج حالياً.")
            return

        for task in tasks:
            order_id, sn, client, dims, file_url, requires_install = task
            with st.expander(f"🖨️ أمر عمل: {sn} | العميل: {client}"):
                st.write(f"**المقاسات:** {dims or '---'}")
                if file_url:
                    st.markdown(f"**ملف التصميم:** [🔗 اضغط هنا لتحميل/مشاهدة التصميم]({file_url})")
                else:
                    st.warning("⚠️ المصمم لم يرفق رابط للتصميم!")
                
                # تحديد المرحلة القادمة بناءً على هل يحتاج تركيب أم لا
                next_stage = "التركيب" if requires_install else "مكتمل"
                btn_text = "✅ إرسال لفريق التركيب" if requires_install else "✅ إنهاء الطلب (جاهز للتسليم)"
                
                if st.button(btn_text, key=f"tech_{order_id}"):
                    status = "نشط" if requires_install else "مكتمل"
                    cursor.execute("UPDATE orders SET current_stage = %s, status = %s WHERE id = %s", (next_stage, status, order_id))
                    conn.commit()
                    st.success(f"🚀 تم تحديث حالة الطلب إلى: {next_stage}")
                    st.rerun()
    except Exception as e:
        st.error(f"خطأ: {e}")