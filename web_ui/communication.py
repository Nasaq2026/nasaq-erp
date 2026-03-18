# web_ui/communication.py
import streamlit as st
import pandas as pd
import urllib.parse

def render_communication(conn):
    st.title("💬 التواصل مع العملاء والمديونيات")
    st.info("💡 هذه الشاشة تحصر جميع المبالغ المتبقية على العملاء وتسمح بإرسال مطالبات مالية احترافية عبر الواتساب.")

    try:
        conn.rollback()
        cursor = conn.cursor()

        # 1. الاستعلام الذكي (نفس منطق الديسكتوب: تجميع الديون لكل عميل)
        query = """
            SELECT 
                client_name AS "اسم العميل", 
                phone AS "رقم الجوال", 
                SUM(total_with_vat - paid) as total_debt,
                string_agg(work_order_sn || ' (' || category || '): متبقي ' || (total_with_vat - paid) || ' ريال', ' | ') as details
            FROM orders 
            WHERE (total_with_vat - paid) > 0
            GROUP BY client_name, phone
            ORDER BY total_debt DESC
        """
        
        # تنفيذ الاستعلام وتحويله لـ DataFrame
        df = pd.read_sql(query, conn)

        if not df.empty:
            # 2. عرض ملخص المديونيات في بطاقات (Metrics)
            total_pending = df['total_debt'].sum()
            st.metric("إجمالي المبالغ المعلقة في السوق 💰", f"{total_pending:,.2f} ر.س", delta="مديونيات عملاء", delta_color="inverse")
            
            st.divider()

            # 3. عرض جدول المديونيات
            # تنسيق عرض المبالغ في الجدول
            display_df = df.copy()
            display_df['total_debt'] = display_df['total_debt'].apply(lambda x: f"{x:,.2f} ر.س")
            
            st.dataframe(display_df[['اسم العميل', 'رقم الجوال', 'total_debt', 'details']], use_container_width=True, hide_index=True)

            st.divider()

            # 4. قسم الإرسال السريع (الواتساب السحري)
            st.markdown("### 📲 إرسال مطالبات مالية سريعة")
            
            for index, row in df.iterrows():
                name = row['اسم العميل']
                phone = row['رقم الجوال']
                debt = row['total_debt']
                details = row['details']
                
                # تظبيط رقم الجوال (تحويل 05 إلى 9665)
                clean_phone = phone.strip()
                if clean_phone.startswith("0"):
                    clean_phone = "966" + clean_phone[1:]

                # صياغة الرسالة الاحترافية (نفس نص الديسكتوب)
                msg = f"مرحباً بك عميلنا العزيز ({name}) في مؤسسة نسق للدعاية والإعلان.\n\n"
                msg += f"نود تذكيركم بلطف أن هنالك مبالغ متبقية على حسابكم بقيمة: *{float(debt):.2f} ريال*.\n\n"
                msg += f"تفاصيل الأعمال المتبقي عليها الدفع:\n{details.replace(' | ', chr(10))}\n\n"
                msg += "نسعد دائماً بخدمتكم، ونتمنى لكم يوماً سعيداً. 🌹"
                
                encoded_msg = urllib.parse.quote(msg)
                wa_link = f"https://wa.me/{clean_phone}?text={encoded_msg}"

                # تصميم صف التواصل
                col_n, col_d, col_b = st.columns([2, 1, 2])
                col_n.markdown(f"👤 **{name}**")
                col_d.markdown(f"🔴 **{debt:,.2f} ر.س**")
                
                # زر الواتساب بتصميم الويب
                col_b.markdown(f"""
                    <a href='{wa_link}' target='_blank' style='display: block; text-align: center; background-color: #25D366; color: white; padding: 8px; border-radius: 5px; text-decoration: none; font-weight: bold; font-size: 14px;'>
                        💬 إرسال مطالبة واتساب
                    </a>
                """, unsafe_allow_html=True)
                st.markdown("<hr style='margin:5px; border-top: 1px solid #333;'>", unsafe_allow_html=True)

        else:
            st.success("🎉 مبروك! لا توجد أي مديونيات متأخرة حالياً.")

    except Exception as e:
        st.error(f"حدث خطأ أثناء جلب المديونيات: {e}")