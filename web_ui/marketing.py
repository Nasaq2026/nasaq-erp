# web_ui/marketing.py
import streamlit as st
import urllib.parse
import pandas as pd

def render_marketing(conn):
    # إعداد الذاكرة المؤقتة لحفظ حالة الإرسال في الجلسة الحالية
    if "sent_clients" not in st.session_state:
        st.session_state.sent_clients = []

    st.markdown("""
        <div style="text-align: right;">
            <h1 style="color: #1e293b;">📢 التسويق وحملات التهاني (Web CRM)</h1>
            <p style="color: #64748b;">أرسل رسائل واتساب مخصصة لعملائك باسمهم لتعزيز الولاء ونشر العروض الجديدة.</p>
        </div>
    """, unsafe_allow_html=True)

    try:
        conn.rollback()
        cursor = conn.cursor()

        # ==========================================
        # 1. إعداد رسالة الحملة
        # ==========================================
        st.markdown("### ✨ تجهيز رسالة الحملة / التهنئة")
        
        st.markdown("""
            <div style='background-color: rgba(245, 158, 11, 0.1); padding: 10px; border-right: 5px solid #f59e0b; border-radius: 8px; margin-bottom: 15px;'>
                <p style='color: #d97706; font-size: 14px; margin: 0;'>💡 <b>نصيحة:</b> استخدم كلمة <b>{اسم_العميل}</b> في الرسالة، وسيقوم النظام باستبدالها تلقائياً باسم كل عميل!</p>
            </div>
        """, unsafe_allow_html=True)
        
        msg_text = st.text_area(
            "نص الرسالة:", 
            "كل عام وأنتم بخير بمناسبة شهر رمضان المبارك يا {اسم_العميل}! يسعدنا في مؤسسة نسق تقديم عروضنا الجديدة...",
            height=120
        )
        
        img_link = st.text_input("🔗 رابط صورة العرض/التهنئة (اختياري):", placeholder="https://example.com/image.jpg")

        st.divider()

        # ==========================================
        # 2. طابور الإرسال (الجدول التفاعلي)
        # ==========================================
        st.markdown("### 👥 طابور الإرسال الذكي")
        
        cursor.execute("SELECT client_name, phone FROM clients WHERE phone IS NOT NULL")
        clients = cursor.fetchall()
        
        if not clients:
            st.warning("⚠️ لا يوجد عملاء مسجلين بأرقام جوال بعد!")
            return

        st.info(f"📋 تم سحب قائمة بـ ({len(clients)}) عميل جاهز للإرسال.")

        # عرض العملاء
        for idx, (name, phone) in enumerate(clients):
            c_name = name or "عميلنا العزيز"
            c_phone = phone.strip()
            
            # تنسيق الرقم الدولي للسعودية
            if c_phone.startswith("0"): 
                c_phone = "966" + c_phone[1:]
                
            # تخصيص الرسالة برمجياً
            personalized_msg = msg_text.replace("{اسم_العميل}", c_name)
            if img_link.strip():
                personalized_msg += f"\n\n📎 لمشاهدة التفاصيل/العرض:\n{img_link}"
                
            encoded_msg = urllib.parse.quote(personalized_msg)
            wa_link = f"https://wa.me/{c_phone}?text={encoded_msg}"
            
            # تصميم الصف التفاعلي
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 2])
                
                with col1:
                    st.markdown(f"👤 **{c_name}**<br><span style='color: #64748b; font-size: 13px;'>{phone}</span>", unsafe_allow_html=True)
                
                with col2:
                    if phone in st.session_state.sent_clients:
                        st.markdown("<p style='color: #10B981; font-weight: bold; padding-top: 10px;'>✅ تم الإرسال</p>", unsafe_allow_html=True)
                    else:
                        st.markdown("<p style='color: #F59E0B; font-weight: bold; padding-top: 10px;'>⏳ في الانتظار</p>", unsafe_allow_html=True)
                
                with col3:
                    # زر الواتساب العصري
                    st.markdown(f"""
                        <a href='{wa_link}' target='_blank' style='display: block; text-align: center; background: linear-gradient(135deg, #25D366 0%, #128C7E 100%); color: white; padding: 10px; border-radius: 12px; text-decoration: none; font-weight: bold; font-size: 13px; box-shadow: 0 4px 10px rgba(37, 211, 102, 0.2);'>
                            💬 إرسال واتساب
                        </a>
                    """, unsafe_allow_html=True)
                    
                    # زر تأكيد الحالة (تحديث width إلى stretch لعام 2026)
                    if phone not in st.session_state.sent_clients:
                        if st.button("تأكيد ✔️", key=f"btn_confirm_{idx}", width="stretch"):
                            st.session_state.sent_clients.append(phone)
                            st.rerun()

                st.markdown("<hr style='margin: 10px 0; border-top: 1px solid #e2e8f0; opacity: 0.3;'>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ حدث خطأ أثناء تحميل بيانات التسويق: {e}")
