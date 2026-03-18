# web_ui/dashboard.py
import streamlit as st
import pandas as pd
import os
import webbrowser
from datetime import datetime

def render_dashboard(conn):
    st.title("📊 لوحة القيادة (Dashboard)")
    st.write(f"مرحباً بك في نظام NASAQ ERP. تاريخ اليوم: {datetime.now().strftime('%Y-%m-%d')}")

    try:
        conn.rollback()
        cursor = conn.cursor()

        # ==========================================
        # 1. جلب الإحصائيات (البطاقات)
        # ==========================================
        cursor.execute("SELECT COUNT(*) FROM orders")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM orders WHERE current_stage='التصميم'")
        design = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM orders WHERE current_stage='الطباعة والإنتاج'")
        print_stage = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM orders WHERE current_stage='التركيب'")
        install = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM orders WHERE status='مكتمل'")
        done = cursor.fetchone()[0]

        # عرض البطاقات بتصميم الـ Metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("إجمالي الطلبات", total)
        col2.metric("في التصميم", design, delta="جاري", delta_color="normal")
        col3.metric("في الإنتاج", print_stage, delta="جاري", delta_color="normal")
        col4.metric("في التركيب", install, delta="ميداني", delta_color="inverse")
        col5.metric("مكتملة ✅", done)

        st.divider()

        # ==========================================
        # 2. قسم التقارير الإدارية
        # ==========================================
        st.markdown("### 📄 التقارير الإدارية ومتابعة الأداء")
        
        with st.expander("📝 عرض وتصدير تقرير أداء فريق العمل", expanded=True):
            st.write("يمكنك معاينة التقرير بالأسفل أو الضغط على الزر لتوليد ملف HTML للطباعة.")
            
            if st.button("🖨️ توليد تقرير أداء فريق العمل للطباعة", use_container_width=True):
                # جلب البيانات للتقرير
                cursor.execute("SELECT work_order_sn, client_name, designer, technician, installer, current_stage, status FROM orders")
                orders = cursor.fetchall()

                # بناء كود HTML الاحترافي (نفس التصميم اللي إنت طالبه)
                html_content = f"""
                <html dir="rtl">
                <head><meta charset="UTF-8"></head>
                <body style="font-family:Tahoma, Arial; padding:30px; background:#f4f6f9;">
                    <div style="background:white; padding:20px; border-radius:10px; box-shadow:0 4px 8px rgba(0,0,0,0.1); max-width: 1000px; margin: auto;">
                        <h1 style="color:#2c3e50; text-align:center;">مؤسسة نسق - تقرير أداء فريق العمل</h1>
                        <p style="text-align:center; color: #7f8c8d;">تاريخ صدور التقرير: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
                        <hr style="border: 0; border-top: 2px solid #3498db;">
                        
                        <table border="1" style="width:100%; border-collapse:collapse; text-align:center; margin-top:20px; font-size: 14px;">
                            <tr style="background:#2980b9; color:white; height:45px;">
                                <th>رقم الأمر</th>
                                <th>العميل</th>
                                <th>المصمم</th>
                                <th>فني الإنتاج</th>
                                <th>عامل التركيب</th>
                                <th>المرحلة الحالية</th>
                                <th>الحالة</th>
                            </tr>
                """
                for o in orders:
                    html_content += f"""
                    <tr style="height:40px;">
                        <td>{o[0]}</td>
                        <td>{o[1]}</td>
                        <td>{o[2] or '---'}</td>
                        <td>{o[3] or '---'}</td>
                        <td>{o[4] or '---'}</td>
                        <td><b>{o[5]}</b></td>
                        <td style="color: {'#27ae60' if o[6]=='مكتمل' else '#e67e22'}">{o[6]}</td>
                    </tr>
                    """
                
                html_content += "</table></div></body></html>"
                
                # في الويب، نعرض زر تحميل للملف بدل فتحه بـ webbrowser (لأن السيرفر قد يكون بعيداً)
                st.download_button(
                    label="📥 اضغط هنا لتحميل ملف التقرير (HTML) وجاهز للطباعة",
                    data=html_content,
                    file_name=f"admin_report_{datetime.now().strftime('%Y%m%d')}.html",
                    mime="text/html",
                    use_container_width=True
                )
                st.success("تم تجهيز التقرير بنجاح!")

        # ==========================================
        # 3. عرض سريع لأحدث الأوامر
        # ==========================================
        st.markdown("### 🕒 أحدث أوامر العمل")
        df_latest = pd.read_sql("SELECT work_order_sn AS \"الأمر\", client_name AS \"العميل\", current_stage AS \"المرحلة\" FROM orders ORDER BY id DESC LIMIT 5", conn)
        st.table(df_latest)

    except Exception as e:
        st.error(f"حدث خطأ في تحميل لوحة القيادة: {e}")