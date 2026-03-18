# web_ui/marketing.py
import streamlit as st
import urllib.parse
import pandas as pd

def render_marketing(conn):
    # إعداد الذاكرة المؤقتة لحفظ حالة الإرسال لكل عميل (عشان ما ينساش لما الصفحة تعمل Refresh)
    if "sent_clients" not in st.session_state:
        st.session_state.sent_clients = []

    st.title("📢 التسويق وحملات التهاني (Web CRM)")
    st.info("💡 استخدم هذه الأداة لإرسال رسائل واتساب مخصصة لعملائك باسمهم. النظام يحتفظ بحالة الإرسال لتجنب التكرار.")

    try:
        conn.rollback()
        cursor = conn.cursor()

        # ==========================================
        # 1. إعداد رسالة الحملة
        # ==========================================
        st.markdown("### ✨ تجهيز رسالة الحملة / التهنئة")
        
        st.markdown("<p style='color: #f59e0b; font-size: 14px;'>💡 نصيحة: استخدم كلمة <b>{اسم_العميل}</b> في الرسالة، وسيقوم النظام باستبدالها تلقائياً باسم كل عميل!</p>", unsafe_allow_html=True)
        
        msg_text = st.text_area(
            "نص الرسالة:", 
            "كل عام وأنتم بخير بمناسبة شهر رمضان المبارك يا {اسم_العميل}! يسعدنا في مؤسسة نسق تقديم عروضنا الجديدة...",
            height=100
        )
        
        img_link = st.text_input("🔗 رابط صورة العرض/التهنئة (اختياري - يظهر كمعاينة في الواتساب):", placeholder="https://example.com/image.jpg")

        st.divider()

        # ==========================================
        # 2. طابور الإرسال (الجدول التفاعلي)
        # ==========================================
        st.markdown("### 👥 طابور إرسال العملاء (آمن ضد الحظر)")
        
        # سحب العملاء من الداتابيز
        cursor.execute("SELECT client_name, phone FROM clients WHERE phone IS NOT NULL")
        clients = cursor.fetchall()
        
        if not clients:
            st.warning("⚠️ لا يوجد عملاء مسجلين بأرقام جوال بعد!")
            return

        st.success(f"تم سحب قائمة بـ ({len(clients)}) عميل بنجاح.")

        # عرض العملاء في شكل بطاقات أو جدول مبسط
        for idx, (name, phone) in enumerate(clients):
            c_name = name or "عميلنا العزيز"
            c_phone = phone.strip()
            
            # تظبيط رقم الجوال للسعودية
            if c_phone.startswith("0"): 
                c_phone = "966" + c_phone[1:]
                
            # تخصيص الرسالة
            personalized_msg = msg_text.replace("{اسم_العميل}", c_name)
            if img_link.strip():
                personalized_msg += f"\n\n📎 لمشاهدة التفاصيل/العرض:\n{img_link}"
                
            # تشفير الرسالة لتناسب الرابط
            encoded_msg = urllib.parse.quote(personalized_msg)
            wa_link = f"https://wa.me/{c_phone}?text={encoded_msg}"
            
            # تصميم الصف
            col1, col2, col3 = st.columns([3, 2, 2])
            
            with col1:
                st.markdown(f"**{c_name}**<br><span style='color: gray; font-size: 13px;'>{phone}</span>", unsafe_allow_html=True)
            
            with col2:
                # التحقق هل تم الإرسال لهذا العميل في الجلسة الحالية أم لا
                if phone in st.session_state.sent_clients:
                    st.markdown("<p style='color: #10B981; font-weight: bold; margin-top: 10px;'>✅ تم الإرسال</p>", unsafe_allow_html=True)
                else:
                    st.markdown("<p style='color: #F59E0B; font-weight: bold; margin-top: 10px;'>⏳ في الانتظار</p>", unsafe_allow_html=True)
            
            with col3:
                # زر إرسال واتساب (مخفي وراء رابط HTML عشان يفتح تاب جديد مباشرة)
                st.markdown(f"""
                    <a href='{wa_link}' target='_blank' style='display: block; text-align: center; background-color: #25D366; color: white; padding: 10px; border-radius: 5px; text-decoration: none; font-weight: bold; margin-top: 5px;'>
                        💬 إرسال واتساب
                    </a>
                """, unsafe_allow_html=True)
                
                # زر تحديث الحالة (عشان المدير يضغط عليه بعد ما يرسل عشان اللون يتغير لأخضر)
                if phone not in st.session_state.sent_clients:
                    if st.button("تأكيد الإرسال ✔️", key=f"btn_confirm_{idx}", use_container_width=True):
                        st.session_state.sent_clients.append(phone)
                        st.rerun() # تحديث الشاشة لتغيير الحالة لـ "تم الإرسال"

            st.markdown("<hr style='margin: 10px 0; border: 0; border-top: 1px solid #333;'>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"حدث خطأ أثناء تحميل بيانات التسويق: {e}")