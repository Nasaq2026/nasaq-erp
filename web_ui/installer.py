import streamlit as st
import pandas as pd
from datetime import datetime

def render_installer(conn, emp_name):
    """واجهة فني التركيبات المتوافقة مع نَسق ERP الجديد"""
    
    st.markdown(f"# 🏗️ منصة التركيبات | الميدان")
    st.info(f"مرحباً بك يا **{emp_name}**، إليك جدول مهامك لليوم.")
    
    if not conn:
        st.error("⚠️ فشل الاتصال بقاعدة البيانات. تأكد من إعدادات السيرفر.")
        return

    try:
        cursor = conn.cursor()
        # 💡 تم تعديل أسماء الأعمدة لتطابق جدول orders في Supabase
        # نستخدم installer بدلاً من installer_name
        query = """
            SELECT id, work_order_sn, client_name, status, current_stage, expected_delivery 
            FROM orders 
            WHERE installer = %s OR installer IS NULL
        """
        cursor.execute(query, (emp_name,))
        rows = cursor.fetchall()
        
        if rows:
            columns = [desc[0] for desc in cursor.description]
            df = pd.DataFrame(rows, columns=columns)
            
            # إحصائيات سريعة
            col1, col2, col3 = st.columns(3)
            with col1:
                pending = len(df[df['status'] != 'تم التركيب'])
                st.metric("مهام متبقية", f"{pending}")
            with col2:
                done = len(df[df['status'] == 'تم التركيب'])
                st.metric("مهام مكتملة", f"{done}")
            with col3:
                st.metric("التاريخ", datetime.now().strftime("%Y-%m-%d"))

            st.divider()

            # عرض المهام
            st.subheader("📋 المهام المسندة إليك")
            for _, row in df.iterrows():
                with st.expander(f"📍 طلب رقم: {row['work_order_sn']} - {row['client_name']}"):
                    c1, c2 = st.columns([2, 1])
                    with c1:
                        st.write(f"**العميل:** {row['client_name']}")
                        st.write(f"**موعد التسليم:** {row['expected_delivery']}")
                        st.write(f"**المرحلة الحالية:** `{row['current_stage']}`")
                        st.write(f"**الحالة:** `{row['status']}`")
                    
                    with c2:
                        new_status = st.selectbox(
                            "تحديث الحالة:",
                            ["قيد التجهيز", "خرج للتركيب", "جاري التركيب", "تم التركيب"],
                            key=f"status_{row['id']}"
                        )
                        
                        if st.button("حفظ التحديث", key=f"btn_{row['id']}", use_container_width=True):
                            try:
                                update_cursor = conn.cursor()
                                # تحديث الحالة والمرحلة معاً
                                update_query = "UPDATE orders SET status = %s, current_stage = 'تركيب' WHERE id = %s"
                                update_cursor.execute(update_query, (new_status, row['id']))
                                conn.commit()
                                st.success("تم التحديث!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"خطأ: {e}")
        else:
            st.info("لا توجد مهام مسجلة باسمك حالياً.")

    except Exception as e:
        st.error(f"⚠️ خطأ في جلب البيانات: {e}")

    # قسم الدعم
    st.write("<br>", unsafe_allow_html=True)
    if st.button("🚨 إرسال إشعار عاجل للإدارة", use_container_width=True):
        st.toast("تم إبلاغ الإدارة بوجود تحديث ميداني.", icon="🔔")
