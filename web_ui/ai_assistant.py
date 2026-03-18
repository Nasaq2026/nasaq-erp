# web_ui/ai_assistant.py
import streamlit as st
import google.generativeai as genai # الطريقة المستقرة والمجربة
import time

def render_ai_assistant():
    st.markdown("""
        <div style="text-align: right; padding: 20px; background: #0c1221; border-radius: 15px; border: 1px solid #38bdf8; margin-bottom: 25px;">
            <h1 style="color: #38bdf8; margin:0;">🤖 مساعد نسق الذكي</h1>
            <p style="color: #94a3b8; font-size: 1.1em;">نظام Gemini المستقر - مؤسسة نسق</p>
        </div>
    """, unsafe_allow_html=True)

    # 1. إعداد العميل
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        # استخدام الموديل الأكثر استقراراً للحسابات المجانية
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception:
        st.warning("⚠️ يرجى ضبط GEMINI_API_KEY في إعدادات Secrets.")
        return

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("بمَ يمكنني مساعدتك في 'نسق' اليوم؟"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            # محاولة الاستدعاء مع معالجة الزحام
            try:
                # إضافة سياق العمل لمؤسسة نسق
                context = f"أنت خبير دعاية وإعلان في نظام NASAQ ERP. الموظف يسألك: {prompt}"
                response = model.generate_content(context)
                
                full_response = response.text
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})

            except Exception as e:
                error_str = str(e)
                if "429" in error_str:
                    st.warning("⏳ جوجل مضغوطة حالياً.. ثواني وبحاول تاني...")
                    time.sleep(10) # انتظار أطول قليلاً لتخطي الزحام
                    try:
                        response = model.generate_content(prompt)
                        message_placeholder.markdown(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
                    except:
                        st.error("⚠️ الحصة المجانية مؤقتاً بالحد الأقصى. جرب تسأل بعد دقيقة يا بطل.")
                else:
                    st.error(f"❌ حدث خطأ غير متوقع: {e}")
