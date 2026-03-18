# web_ui/ai_assistant.py
import streamlit as st
from google import genai
from google.genai import types
import time

def render_ai_assistant():
    st.markdown("""
        <div style="text-align: right; padding: 20px; background: #0c1221; border-radius: 15px; border: 1px solid #38bdf8; margin-bottom: 25px;">
            <h1 style="color: #38bdf8; margin:0;">🤖 مساعد نسق الذكي</h1>
            <p style="color: #94a3b8; font-size: 1.1em;">مدعوم بتقنية Gemini 1.5 Flash السريعة</p>
        </div>
    """, unsafe_allow_html=True)

    # 1. إعداد العميل (Client)
    try:
        if "GEMINI_API_KEY" not in st.secrets:
            st.error("❌ لم يتم العثور على مفتاح API في Secrets. يرجى ضبط GEMINI_API_KEY.")
            return
        
        api_key = st.secrets["GEMINI_API_KEY"]
        client = genai.Client(api_key=api_key)
        # تحديد الموديل المستقر والسريع
        MODEL_NAME = "gemini-1.5-flash"
    except Exception as e:
        st.error(f"⚠️ خطأ في تهيئة النظام: {e}")
        return

    # 2. إدارة ذاكرة المحادثة
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # عرض الرسائل السابقة
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 3. محرك المحادثة مع معالجة ذكية للضغط
    if prompt := st.chat_input("اسألني عن أفكار تصاميم، محتوى إعلاني، أو تحليل بيانات..."):
        # عرض رسالة المستخدم وحفظها
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            # محاولة الاستدعاء مع معالجة خطأ الزحام (429)
            try:
                # تعليمات النظام لضبط الشخصية المهنية لمؤسسة نسق
                sys_instruct = "أنت خبير دعاية وإعلان ومساعد ذكي مدمج في نظام NASAQ ERP. أجب بلهجة مهنية سعودية/سودانية ودودة، وساعد الموظفين في أفكار اللوجوهات، خامات الطباعة، وتنسيق الألوان."
                
                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=sys_instruct,
                        temperature=0.7
                    )
                )
                
                full_response = response.text
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})

            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg:
                    st.warning("⏳ يبدو أن هناك ضغطاً على الخدمة المجانية حالياً. سأحاول مرة أخرى تلقائياً بعد قليل...")
                    time.sleep(5) # انتظار بسيط للمحاولة التلقائية
                    try:
                        # محاولة ثانية
                        response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
                        message_placeholder.markdown(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
                    except:
                        st.error("⚠️ جوجل تطلب منك الانتظار لدقيقة واحدة بسبب كثرة الطلبات. خذ استراحة قصيرة وجرب مرة أخرى!")
                elif "404" in error_msg:
                    st.error("❌ الموديل غير متاح حالياً. يرجى التأكد من اسم الموديل أو تحديث المكتبة.")
                else:
                    st.error(f"❌ حدث خطأ غير متوقع: {e}")
