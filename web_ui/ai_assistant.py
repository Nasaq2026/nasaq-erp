import streamlit as st
import google.generativeai as genai

# ✅ إضافة conn كمتغير افتراضي لمنع خطأ TypeError
def render_ai_assistant(conn=None): 
    st.markdown("""
        <div style="text-align: right; padding: 20px; background: #0c1221; border-radius: 15px; border: 1px solid #38bdf8; margin-bottom: 25px;">
            <h1 style="color: #38bdf8; margin:0;">🤖 مساعد نَسق الذكي</h1>
            <p style="color: #94a3b8; font-size: 1.1em;">نظام الربط الذكي - مؤسسة نَسق</p>
        </div>
    """, unsafe_allow_html=True)

    # 1. إعداد العميل (Gemini)
    try:
        # تأكد أنك أضفت GEMINI_API_KEY في secrets.toml على Streamlit Cloud
        if "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
            genai.configure(api_key=api_key)
            
            if "working_model" not in st.session_state:
                available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                flash_models = [m for m in available_models if "flash" in m.lower()]
                st.session_state.working_model = flash_models[0] if flash_models else available_models[0]
            
            model = genai.GenerativeModel(st.session_state.working_model)
        else:
            st.error("⚠️ مفتاح API غير موجود في الإعدادات (Secrets).")
            return
    except Exception as e:
        st.error(f"⚠️ خطأ في الاتصال بجوجل: {e}")
        return

    # 2. إدارة الذاكرة
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 3. محرك المحادثة
    if prompt := st.chat_input("اسألني أي شيء عن 'نَسق'..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                # يمكنك لاحقاً استخدام conn هنا لسحب بيانات حقيقية من الجدول
                full_prompt = f"أنت مساعد نظام NASAQ ERP للدعاية والإعلان. العميل يسألك: {prompt}"
                response = model.generate_content(full_prompt)
                
                if response.text:
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"⚠️ عذراً، حدث خطأ: {e}")
