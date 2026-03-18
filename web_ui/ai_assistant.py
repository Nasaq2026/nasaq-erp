# web_ui/ai_assistant.py
import streamlit as st
from google import genai
from google.genai import types

def render_ai_assistant():
    st.markdown("""
        <div style="text-align: right; padding: 20px; background: #0c1221; border-radius: 15px; border: 1px solid #38bdf8;">
            <h1 style="color: #38bdf8; margin:0;">🤖 مساعد نسق الذكي</h1>
            <p style="color: #94a3b8;">متصل بـ Google Gemini 2.0 Flash</p>
        </div>
    """, unsafe_allow_html=True)

    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        client = genai.Client(api_key=api_key)
    except:
        st.warning("⚠️ تأكد من ضبط GEMINI_API_KEY في Streamlit Secrets.")
        return

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("اسألني أي شيء عن تصاميم 'نسق'..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            # 💡 السر هنا: بنجرب الموديل الجديد بالاسم المختصر "gemini-2.0-flash" 
            # لو ما اشتغلش بنجرب "gemini-1.5-flash"
            models_to_try = ["gemini-2.0-flash", "gemini-1.5-flash"]
            
            response_text = ""
            for model_name in models_to_try:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            system_instruction="أنت خبير دعاية وإعلان في نظام NASAQ ERP. أجب بلهجة ودودة ومحترفة.",
                            temperature=0.7
                        )
                    )
                    response_text = response.text
                    break # لو نجح، نخرج من الحلقة
                except Exception as e:
                    if model_name == models_to_try[-1]: # لو ده آخر موديل وفشل
                        st.error(f"❌ عذراً، جميع المحاولات فشلت: {e}")
                    continue # جرب الموديل اللي بعده

            if response_text:
                st.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
