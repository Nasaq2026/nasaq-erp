# web_ui/ai_assistant.py
import streamlit as st
from google import genai
from google.genai import types
import time # 👈 أضفنا الوقت

def render_ai_assistant():
    # ... (نفس كود التصميم اللي عندك) ...

    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        client = genai.Client(api_key=api_key)
        
        # اختيار الموديل الأكثر استقراراً للحصة المجانية
        MODEL_NAME = "gemini-1.5-flash" # 👈 جرب ده لو الـ 2.0 عليه ضغط
    except:
        st.warning("⚠️ تأكد من إعداد المفتاح في Secrets.")
        return

    # ... (كود عرض الرسائل) ...

    if prompt := st.chat_input("اسألني أي شيء..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                response = client.models.generate_content(
                    model=MODEL_NAME, 
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction="أنت مساعد في نظام NASAQ ERP.",
                        temperature=0.7,
                    )
                )
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            
            except Exception as e:
                if "429" in str(e):
                    st.error("⚠️ جوجل مضغوطة حالياً (حصتك المجانية مؤقتاً). انتظر 30 ثانية وجرب تاني يا بطل.")
                else:
                    st.error(f"❌ خطأ: {e}")
