# web_ui/ai_assistant.py
import streamlit as st
from google import genai
from google.genai import types

def render_ai_assistant():
    st.markdown("""
        <div style="text-align: right; padding: 20px; background: #0c1221; border-radius: 15px; border: 2px solid #38bdf8;">
            <h1 style="color: #38bdf8; margin:0;">🤖 مساعد نسق الذكي</h1>
            <p style="color: #94a3b8;">نظام Gemini 2.0 المتطور - مؤسسة نسق</p>
        </div>
    """, unsafe_allow_html=True)

    # 1. جلب المفتاح من Secrets
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        # تعريف العميل (Client)
        client = genai.Client(api_key=api_key)
    except Exception as e:
        st.error("⚠️ لم يتم العثور على مفتاح API في إعدادات Secrets.")
        return

    # 2. إدارة ذاكرة الشات
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 3. محرك المحادثة
    if prompt := st.chat_input("اسألني عن أفكار تصاميم 'نسق' أو محتوى إعلاني..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                # 💡 الحل هنا: نستخدم الاسم الصافي للموديل "gemini-2.0-flash" 
                # المكتبة الجديدة بتضيف المسارات تلقائياً، فلا تكتب models/
                response = client.models.generate_content(
                    model="gemini-2.0-flash", 
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction="أنت مساعد ذكي خبير في الدعاية والإعلان وتعمل في نظام NASAQ ERP. أجب بلهجة مهنية ودودة ومختصرة.",
                        temperature=0.8,
                    )
                )
                
                if response and response.text:
                    full_response = response.text
                    st.markdown(full_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                else:
                    st.warning("⚠️ استلمت رداً فارغاً من الذكاء الاصطناعي، حاول مرة أخرى.")

            except Exception as e:
                # معالجة ذكية للخطأ 404 أو 429
                if "404" in str(e):
                    st.error("❌ الموديل غير متوفر حالياً بهذا الاسم. جاري تجربة الموديل البديل...")
                    # محاولة أخيرة بموديل 1.5 بالاسم الصافي
                    try:
                        resp_alt = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
                        st.markdown(resp_alt.text)
                        st.session_state.messages.append({"role": "assistant", "content": resp_alt.text})
                    except:
                        st.error("⚠️ فشلت جميع محاولات الاتصال بالموديلات المتاحة.")
                elif "429" in str(e):
                    st.error("⏳ ضغط عالي على الخدمة المجانية. انتظر 20 ثانية وجرب تاني يا بطل.")
                else:
                    st.error(f"⚠️ حدث خطأ غير متوقع: {e}")
