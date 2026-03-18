def inject_creative_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');

    /* التنسيق العام والخط */
    html, body, [data-testid="stSidebar"] *, .stMarkdown {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl; 
        text-align: right;
    }

    /* --- 🌑 القائمة الجانبية (Dark Sidebar) --- */
    [data-testid="stSidebar"] {
        background: #0c1221 !important;
        border-left: 1px solid rgba(56, 189, 248, 0.1);
    }

    /* --- 🚫 إزالة الدوائر البيضاء نهائياً --- */
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label div[data-testid="stRadioButtonCustomObject"] {
        display: none !important;
    }

    /* --- ✨ تنسيق النصوص (أبيض ناصع دائماً) --- */
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
        color: #ffffff !important; /* لون النص أبيض ناصع */
        background-color: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        padding: 14px 20px !important;
        border-radius: 12px !important;
        margin-bottom: 10px !important;
        transition: all 0.3s ease-in-out;
        cursor: pointer;
        display: flex;
        align-items: center;
        width: 100% !important;
        font-weight: 600 !important;
    }

    /* --- 💡 تأثير الماوس (Hover) --- */
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
        background-color: rgba(56, 189, 248, 0.1) !important;
        border-color: rgba(56, 189, 248, 0.4) !important;
        color: #38bdf8 !important; /* النص ينور سماوي عند المرور فوقه */
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.2);
    }

    /* --- 🎯 عند اختيار العنصر (Active) --- */
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[data-selected="true"] {
        background: rgba(56, 189, 248, 0.15) !important;
        border-color: #38bdf8 !important;
        color: #ffffff !important; /* يظل النص أبيض ناصع حتى بعد الاختيار */
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.3);
        font-weight: 700 !important;
    }

    /* إخفاء شعار Streamlit العلوي */
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)
