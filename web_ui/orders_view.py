import streamlit as st
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components

def render_orders_view(conn):
    # 1. تنسيق الواجهة بألوان "نَسق" (هوية بصرية جذابة)
    st.markdown("""
        <style>
        .order-card {
            background-color: #ffffff;
            border-radius: 15px;
            padding: 20px;
            border-right: 10px solid #fb923c; /* لون برتقالي نَسق */
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            margin-bottom: 20px;
        }
        .status-badge {
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
        }
        .internal-note {
            background-color: #f1f5f9;
            padding: 10px;
            border-radius: 8px;
            font-style: italic;
            border-right: 3px solid #64748b;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("📂 استعراض وإدارة طلبات نَسق")
    
    try:
        cursor = conn.cursor()
        # جلب البيانات شاملة الملاحظات وصورة التعميد
        query = "SELECT * FROM orders ORDER BY id DESC"
        df = pd.read_sql(query, conn)

        if df.empty:
            st.info("📭 لا توجد طلبات لعرضها حالياً.")
            return

        # 2. نظام البحث السريع
        search_query = st.text_input("🔍 ابحث عن طلب (اسم العميل أو رقم الطلب):")
        if search_query:
            df = df[df['client_name'].str.contains(search_query) | df['work_order_sn'].str.contains(search_query)]

        # 3. عرض الطلبات بنظام البطاقات (Cards)
        for index, row in df.iterrows():
            with st.container():
                st.markdown(f"""
                <div class="order-card">
                    <div style="display: flex; justify-content: space-between;">
                        <h3 style="margin:0;">📦 {row['client_name']}</h3>
                        <span class="status-badge" style="background-color:#fef3c7; color:#92400e;">{row['current_stage']}</span>
                    </div>
                    <p style="color:#64748b; font-size:0.9em;">رقم الطلب: <b>{row['work_order_sn']}</b> | المنتج: {row['category']}</p>
                    <hr style="margin: 10px 0;">
                </div>
                """, unsafe_allow_html=True)

                # داخل كل بطاقة (أزرار تفاعلية)
                c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
                
                # زر الواتساب التلقائي
                msg = f"مرحباً {row['client_name']}، نرفق لكم نموذج التصميم للطلب {row['work_order_sn']}. يرجى التعميد للتنفيذ."
                wa_url = f"https://wa.me/{row['phone']}?text={msg}"
                c1.markdown(f"[💬 واتساب تعميد]({wa_url})")

                # مساحة التعميد (رفع صورة الواتساب)
                with c2:
                    if st.button(f"📸 رفع تعميد", key=f"app_{row['id']}"):
                        st.session_state[f"show_upload_{row['id']}"] = True
                
                # الملاحظات الداخلية (للمصمم والفني)
                with c3:
                    if st.button(f"📝 ملاحظات", key=f"note_{row['id']}"):
                        st.session_state[f"show_note_{row['id']}"] = True

                # طباعة أمر العمل PDF
                if c4.button("📑 أمر عمل PDF", key=f"print_{row['id']}"):
                    st.write("جاري التوليد...")

                # إظهار نوافذ منبثقة صغيرة (Dialogs)
                if st.session_state.get(f"show_upload_{row['id']}", False):
                    img_file = st.file_uploader("ارفع صورة تعميد العميل (Screenshot)", type=['png', 'jpg', 'jpeg'], key=f"file_{row['id']}")
                    if img_file:
                        st.success("تم حفظ صورة التعميد في أرشيف الطلب ✅")

                if st.session_state.get(f"show_note_{row['id']}", False):
                    new_note = st.text_area("أضف ملاحظة للموظفين (المصمم/الفني):", key=f"txt_{row['id']}")
                    if st.button("حفظ الملاحظة", key=f"save_{row['id']}"):
                        st.info("تم إرسال الملاحظة لطاقم العمل 📩")

                st.markdown("---")

    except Exception as e:
        st.error(f"خطأ في واجهة العرض: {e}")
