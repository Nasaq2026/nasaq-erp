# web_ui/ai_assistant.py
import streamlit as st
from google import genai # 👈 المكتبة الجديدة المعتمدة في 2026
import os

def render_ai_assistant():
    st.markdown("""
        <div style="text-align: right;">
            <h1 style="color: #38bdf8;">🤖 مساعد نسق الذكي (Gemini 2.0)</h1>
            <p style="color: #64748b;">أنا هنا لمساعدتك باستخدام أحدث تقنيات الذكاء الاصطناعي من جوجل.</p>
        </div>
    """, unsafe_allow_html=True)

    # إعداد العميل (Client) باستخدام المكتبة الجديدة
    # يُفضل وضع المفتاح في st.secrets لضمان الأمان
    try:
        api_key = st.secrets["GEMINI_API_KEY"] if "GEMINI_API_KEY" in st.secrets else "ضغ_مفتاحك_هنا"
        client = genai.Client(api_key=api_key)
    except Exception as e:
        st.error("❌ لم يتم العثور على مفتاح API. تأكد من إعداده في Secrets.")
        return

    # تهيئة الذاكرة (Session State)
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # عرض المحادثات السابقة
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # واجهة إدخال الشات
    if prompt := st.chat_input("اسألني عن أفكار تصاميم، أو محتوى إعلاني لـ 'نسق'..."):
        # إضافة رسالة المستخدم للذاكرة والعرض
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # طلب الرد من Gemini باستخدام الطريقة الجديدة generate
        with st.chat_message("assistant"):
            try:
                # إضافة سياق (Context) لجعل الردود متخصصة في الدعاية والإعلان
                system_instruction = "أنت خبير في الدعاية والإعلان وتعمل كمساعد ذكي داخل نظام NASAQ ERP. ساعد الموظفين بلهجة مهنية وودودة."
                
                response = client.models.generate_content(
                    model="gemini-2.0-flash", # أو gemini-1.5-pro حسب رغبتك
                    contents=prompt,
                    config=genai.types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.7
                    )
                )
                
                full_response = response.text
                st.markdown(full_response)
                
                # حفظ الرد في الذاكرة
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            
            except Exception as e:
                st.error(f"⚠️ فشل الاتصال بالذكاء الاصطناعي: {e}")
