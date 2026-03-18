def inject_creative_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');

    /* 1. التنسيق العام والخط */
    html, body, [data-testid="stSidebar"] *, .stMarkdown {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl; 
        text-align: right;
    }

    /* 2. 🌑 القائمة الجانبية (Dark Sidebar) */
    [data-testid="stSidebar"] {
        background: #0c1221 !important;
    }

    /* --- 🚫 إزالة الدوائر البيضاء نهائياً --- */
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label div[data-testid="stRadioButtonCustomObject"] {
        display: none !important;
    }

    /* --- ✨ جعل نصوص الخيارات باللون الأبيض الناصع (مهم جداً) --- */
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p {
        color: #ffffff !important; /* أبيض ناصع 100% */
        font-size: 16px !important;
        font-weight: 600 !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* --- 💖 تصميم كرت الخيار (The Button Card) --- */
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
        background-color: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        padding: 15px 20px !important;
        border-radius: 12px !important;
        margin-bottom: 12px !important;
        display: flex;
        align-items: center;
        transition: all 0.3s ease;
        cursor: pointer;
        width: 100% !important;
    }

    /* --- 💡 تأثير الماوس (Hover) --- */
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
        background-color: rgba(56, 189, 248, 0.1) !important;
        border-color: rgba(56, 189, 248, 0.4) !important;
        transform: translateX(-5px);
    }

    /* --- 🎯 عند اختيار القسم (Active State) --- */
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[data-selected="true"] {
        background: rgba(56, 189, 248, 0.15) !important;
        border-color: #38bdf8 !important; /* إطار أزرق نيون */
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.2);
    }

    /* إخفاء شعار Streamlit العلوي */
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)
