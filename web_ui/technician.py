# web_ui/technician.py
import streamlit as st

def render_technician(conn, emp_name):
    st.markdown(f"""
        <div style="text-align: right;">
            <h1 style="color: #1e293b;">🖨️ قسم الإنتاج والطباعة</h1>
            <p style="color: #64748b;">أهلاً بك يا <b>{emp_name}</b>. الطلبات الجاهزة للتنفيذ والطباعة:</p>
        </div>
    """, unsafe_allow_html=True)
    
    try:
        conn.rollback()
        cursor = conn.cursor()
        
        # جلب المهام المسندة للفني
        cursor.execute("""
            SELECT id, work_order_sn, client_name, dimensions, file_url, requires_install 
            FROM orders 
            WHERE current_stage = 'الطباعة والإنتاج' AND status = 'نشط' AND technician = %s
            ORDER BY id ASC
        """, (emp_name,))
        tasks = cursor.fetchall()
        
        if not tasks:
            st.success("🎉 لا توجد مهام إنتاج حالياً. استمر في التميز!")
            return

        for task in tasks:
            order_id, sn, client, dims, file_url, requires_install = task
            
            with st.expander(f"🖨️ أمر عمل: {sn} | العميل: {client}", expanded=True):
                col_info1, col_info2 = st.columns(2)
                col_info1.markdown(f"**📏 المقاسات:**\n`{dims if dims else 'غير محدد'}`")
                
                # تنسيق رابط التصميم بشكل احترافي
                if file_url:
                    col_info2.markdown(f"""
                        **🎨 ملف التصميم:**
                        <a href='{file_url}' target='_blank' style='display: inline-block; background-color: #0ea5e9; color: white; padding: 5px 15px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 13px;'>
                            🔗 فتح رابط التصميم
                        </a>
                    """, unsafe_allow_html=True)
                else:
                    col_info2.warning("⚠️ لا يوجد رابط تصميم مرفق!")
                
                st.markdown("<br>", unsafe_allow_html=True)

                # تحديد المرحلة القادمة ذكياً
                next_stage = "التركيب" if requires_install else "جاهز للتسليم"
                btn_text = "✅ إنهاء الطباعة وإرسال للتركيب" if requires_install else "✅ إنهاء الطباعة (جاهز للتسليم)"
                
                # ✅ تحديث الزر للكود الجديد width="stretch"
                if st.button(btn_text, key=f"tech_{order_id}", width="stretch"):
                    final_status = "نشط" if requires_install else "مكتمل"
                    cursor.execute("""
                        UPDATE orders 
                        SET current_stage = %s, status = %s 
                        WHERE id = %s
                    """, (next_stage, final_status, order_id))
                    conn.commit()
                    st.success(f"🚀 تم التحويل إلى: {next_stage}")
                    st.balloons()
                    st.rerun()

    except Exception as e:
        st.error(f"❌ حدث خطأ في واجهة الفني: {e}")
