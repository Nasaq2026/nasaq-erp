# web_ui/ai_assistant.py
import streamlit as st
from google import genai
from google.genai import types
import time

def render_ai_assistant():
    st.markdown("""
        <div style="text-align: right; padding: 20px; background: #0c1221; border-radius: 15px; border: 1px solid #38bdf8; margin-bottom: 25px;">
            <h1 style="color: #38bdf8; margin:0;">🤖 مساعد نسق الذكي</h1>
            <p style="color: #94a3b8; font-size: 1.1em;">نظام الربط المتطور - مؤسسة نسق</p>
        </div>
    """, unsafe_allow_html=True)

    # 1. إعداد العميل (Client)
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        client = genai.Client(api_key=api_key)
    except Exception:
        st.warning("⚠️ يرجى ضبط GEMINI_API_KEY في إعدادات Secrets.")
        return

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("كيف أساعدك في 'نسق' اليوم؟"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            # 💡 مصفوفة الأسماء المحتملة للموديل (لضمان تجاوز الـ 404)
            # جربنا الأسماء اللي جوجل بتغيرها كل شوية
            possible_models = ["gemini-1.5-flash", "gemini-1.5-flash-002", "gemini-2.0-flash"]
            
            response_text = ""
            success = False
            
            for model_id in possible_models:
                try:
                    response = client.models.generate_content(
                        model=model_id,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            system_instruction="أنت خبير في الدعاية والإعلان وتعمل في نظام NASAQ ERP. أجب بلهجة مهنية ودودة ومختصرة.",
                            temperature=0.7
                        )
                    )
                    response_text = response.text
                    success = True
                    break # نجحنا! نخرج من الحلقة
                except Exception as e:
                    # لو الخطأ زحمة (429) ننتظر ونحاول تاني بنفس الموديل
                    if "429" in str(e):
                        with st.spinner("⏳ زحمة بسيطة.. ثواني وبحاول تاني..."):
                            time.sleep(5)
                            try:
                                response = client.models.generate_content(model=model_id, contents=prompt)
                                response_text = response.text
                                success = True
                                break
                            except: continue
                    # لو الخطأ (404) نجرب الموديل اللي بعده في القائمة
                    continue

            if success:
                st.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
            else:
                st.error("❌ عذراً، يبدو أن هناك مشكلة مؤقتة في سيرفرات جوجل. جرب مرة أخرى بعد دقيقة.")
