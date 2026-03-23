import streamlit as st
import pandas as pd
from datetime import datetime

def render_installer(conn, emp_name):
    """واجهة فني التركيبات المحدثة لعام 2026"""
    
    # --- العناوين الرئيسية ---
    st.markdown(f"# 🏗️ منصة التركيبات | الميدان")
    st.write(f"مرحباً بك يا **{emp_name}**، إليك جدول مهامك لليوم.")
    
    if not conn:
        st.error("⚠️ فشل الاتصال بقاعدة البيانات. تأكد من إعدادات السيرفر.")
        return

    # --- 1. إحصائيات سريعة للفني ---
    try:
        cursor = conn.cursor()
        # جلب المهام (بفرض وجود عمود باسم installer_name في جدول orders)
        query = "SELECT id, client_name, project_name, status, delivery_date FROM orders WHERE installer_name = %s"
        cursor.execute(query, (emp_name,))
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(rows, columns=columns)
        
        # إحصائيات بسيطة
        col1, col2, col3 = st.columns(3)
        with col1:
            pending = len(df[df['status'] != 'تم التركيب'])
            st.metric("مهام متبقية", f"{pending} طلبات")
        with col2:
            done = len(df[df['status'] == 'تم التركيب'])
            st.metric("مهام مكتملة", f"{done}")
        with col3:
            st.metric("تاريخ اليوم", datetime.now().strftime("%Y-%m-%d"))

    except Exception as e:
        st.error(f"خطأ في جلب البيانات: {e}")
        return

    st.divider()

    # --- 2. إدارة المهام الحالية ---
    st.subheader("📋 المهام المسندة إليك")
    
    if df.empty:
        st.info("لا توجد مهام مسجلة باسمك حالياً. استمتع بوقتك!")
    else:
        for index, row in df.iterrows():
            with st.expander(f"📍 {row['project_name']} - {row['client_name']}"):
                c1, c2 = st.columns([2, 1])
                with c1:
                    st.write(f"**رقم الطلب:** {row['id']}")
                    st.write(f"**تاريخ التسليم المتوقع:** {row['delivery_date']}")
                    st.write(f"**الحالة الحالية:** `{row['status']}`")
                
                with c2:
                    # تحديث الحالة
                    new_status = st.selectbox(
                        "تحديث الحالة إلى:",
                        ["قيد التجهيز", "خرج للتركيب", "جاري التركيب", "تم التركيب"],
                        key=f"status_{row['id']}"
                    )
                    
                    if st.button("تحديث الآن", key=f"btn_{row['id']}", use_container_width=True):
                        try:
                            update_cursor = conn.cursor()
                            update_query = "UPDATE orders SET status = %s WHERE id = %s"
                            update_cursor.execute(update_query, (new_status, row['id']))
                            conn.commit()
                            st.success(f"تم تحديث الطلب #{row['id']} بنجاح!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"فشل التحديث: {e}")

    # --- 3. قسم الدعم الفني ---
    st.write("<br><br>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("### 📞 هل تواجه مشكلة في الموقع؟")
        st.write("إذا واجهت أي معوقات فنية أو احتجت للتواصل مع الإدارة:")
        if st.button("إرسال إشعار للمدير", use_container_width=True):
            st.toast("تم إرسال إشعار للإدارة، سيتم التواصل معك فوراً.", icon="📩")
