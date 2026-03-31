import streamlit as st
import google.generativeai as genai
from utils.db_manager import db

def render_ai(conn):
    st.title("🤖 نَسق AI | مستشارك الذكي")
    st.subheader("تحليل البيانات واقتراحات النمو")

    # 1. إعداد مفتاح API (يجب أن يكون في Secrets)
    if "GOOGLE_API_KEY" not in st.secrets:
        st.error("⚠️ يرجى إضافة GOOGLE_API_KEY في إعدادات Streamlit Secrets.")
        return

    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')

    # 2. جلب ملخص البيانات لتقديمها للذكاء الاصطناعي
    stats = db.execute_query("""
        SELECT 
            COUNT(*) as total_orders, 
            SUM(total) as total_revenue,
            category, 
            COUNT(category) as cat_count
        FROM orders 
        GROUP BY category
    """, fetch=True)

    if not stats:
        st.info("📊 لا توجد بيانات كافية للتحليل حالياً. ابدأ بإضافة طلبات جديدة!")
        return

    # 3. واجهة الدردشة مع البيانات
    st.markdown("---")
    user_question = st.text_input("اسأل نَسق AI عن عملك (مثلاً: كيف أزيد مبيعات لوحات الكانفاس؟)")

    if st.button("تحليل واستشارة ✨"):
        with st.spinner("جاري تحليل البيانات وتحضير الإجابة..."):
            # تحويل البيانات لنص يفهمه الذكاء الاصطناعي
            context = f"بيانات المؤسسة الحالية: إجمالي الطلبات {stats[0]['total_orders']}، الإيرادات {stats[0]['total_revenue']}. الأقسام الأكثر طلباً: {stats}."
            
            prompt = f"""
            أنت مستشار أعمال خبير في مجال الدعاية والإعلان والطباعة. 
            بناءً على هذه البيانات: {context}
            أجب على سؤال المستخدم التالي باحترافية وبلهجة سعودية ودية: {user_question}
            """
            
            response = model.generate_content(prompt)
            st.markdown("### 💡 نصيحة نَسق AI:")
            st.write(response.text)

    # 4. قسم الإحصائيات السريعة
    st.sidebar.markdown("### 📈 نظرة سريعة")
    for row in stats:
        st.sidebar.write(f"{row['category']}: {row['cat_count']} طلب")
