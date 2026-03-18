# web_ui/ai_assistant.py
import streamlit as st
import google.generativeai as genai

def render_ai_assistant():
    st.markdown("""
        <div style="text-align: right;">
            <h1 style="color: #38bdf8;">🤖 مساعد نسق الذكي (Gemini)</h1>
            <p style="color: #64748b;">أنا هنا لمساعدتك في أفكار التصميم، كتابة محتوى الإعلانات، أو تحليل بيانات ورشتك.</p>
        </div>
    """, unsafe_allow_html=True)

    # إعداد مفتاح API (يُفضل وضعه في Secrets)
    # ملاحظة: احصل على مفتاحك من Google AI Studio
    API_KEY = "ضغ_مفتاح_API_الخاص_بك_هنا" 
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-pro')

    # تهيئة ذاكرة الشات في الـ Session State
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # عرض الرسائل السابقة بتصميم زجاجي
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # استقبال مدخلات المستخدم
    if prompt := st.chat_input("كيف يمكنني مساعدتك في 'نسق' اليوم؟"):
        # عرض رسالة المستخدم
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # توليد رد من جيمناي
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            try:
                # إضافة سياق لـ Gemini عشان يعرف إنه شغال في مؤسسة نسق
                context = f"أنت مساعد ذكي مدمج في نظام NASAQ ERP لمؤسسة دعاية وإعلان. الموظف يسألك: {prompt}"
                response = model.generate_content(context)
                full_response = response.text
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                st.error(f"❌ عذراً، حدث خطأ في الاتصال بـ Gemini: {e}")
