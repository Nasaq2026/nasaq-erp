# web_ui/installer.py
import streamlit as st

def render_installer(conn, emp_name):
    st.markdown(f"""
        <div style="text-align: right;">
            <h1 style="color: #1e293b;">🚛 قسم التركيبات الميدانية</h1>
            <p style="color: #64748b;">أهلاً بك يا <b>{emp_name}</b>. المهام المطلوب تنفيذها في الموقع:</p>
        </div>
    """, unsafe_allow_html=True)

    try:
        conn.rollback()
        cursor = conn.cursor()
        
        # جلب المهام المسندة لفريق التركيب
        cursor.execute("""
            SELECT id, work_order_sn, client_name, dimensions, details, material_type 
            FROM orders 
            WHERE current_stage = 'التركيب' AND status = 'نشط' AND installer = %s
            ORDER BY id ASC
        """, (emp_name,))
        tasks = cursor.fetchall()

        if not tasks:
            st.success("🎉 لا توجد مهام تركيب حالياً. بالتوفيق في طريقك!")
            return

        for task in tasks:
            order_id, sn, client, dims, details, mat = task
            
            with st.expander(f"🚛 تركيب أمر: {sn} | العميل: {client}", expanded=True):
                st.markdown(f"**📏 المقاسات:** `{dims if dims else '---'}`")
                st.markdown(f"**💎 نوع الخامة:** `{mat if mat else '---'}`")
                st.info(f"📝 **تفاصيل التركيب:** {details if details else 'لا توجد ملاحظات إضافية.'}")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # ✅ زر إنهاء المهمة بالكود الجديد width="stretch"
                if st.button(f"✅ تم التركيب بنجاح (إغلاق الطلب)", key=f"inst_{order_id}", width="stretch"):
                    cursor.execute("""
                        UPDATE orders 
                        SET current_stage = 'مكتمل', status = 'مكتمل' 
                        WHERE id = %s
                    """, (order_id,))
                    conn.commit()
                    st.success(f"🚀 كفو! تم إنهاء الطلب {sn} بنجاح.")
                    st.balloons()
                    st.rerun()

    except Exception as e:
        st.error(f"❌ حدث خطأ في واجهة التركيب: {e}")
