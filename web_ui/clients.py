# web_ui/clients.py
import streamlit as st
import pandas as pd

def render_clients(conn):
    st.markdown("""
        <div style="text-align: right;">
            <h1 style="color: #1e293b;">👥 إدارة العملاء (CRM)</h1>
            <p style="color: #64748b;">قائمة العملاء، البيانات الضريبية، ومتابعة مستوى الولاء (VIP).</p>
        </div>
    """, unsafe_allow_html=True)

    try:
        conn.rollback()
        cursor = conn.cursor()

        # 1. سحب البيانات
        query = """
            SELECT 
                id AS "الرقم", 
                client_name AS "اسم العميل", 
                phone AS "رقم الجوال", 
                COALESCE(tax_number, 'غير مسجل') AS "الرقم الضريبي", 
                COALESCE(cr_number, 'غير مسجل') AS "السجل التجاري", 
                COALESCE(national_address, 'غير مسجل') AS "العنوان الوطني", 
                orders_count AS "عدد الطلبات"
            FROM clients 
            ORDER BY id DESC
        """
        df = pd.read_sql(query, conn)

        if not df.empty:
            # 2. إضافة لمسة الـ VIP الذكية
            def apply_vip_status(row):
                count = row["عدد الطلبات"]
                if count >= 3:
                    return f"{count} 🌟"
                return str(count)

            # عمل نسخة للعمل عليها لتجنب تحذيرات Pandas
            df_display = df.copy()
            df_display["عدد الطلبات"] = df_display.apply(apply_vip_status, axis=1)

            # 3. عرض الجدول بتنسيق ويب متجاوب (كود 2026 المحدث)
            st.dataframe(
                df_display, 
                width="stretch", 
                hide_index=True,
                column_config={
                    "رقم الجوال": st.column_config.TextColumn("رقم الجوال"),
                    "عدد الطلبات": st.column_config.TextColumn("عدد الطلبات", help="العملاء الذين لديهم 3 طلبات أو أكثر يحصلون على وسم VIP 🌟")
                }
            )

            # 4. إحصائية سريعة أسفل الجدول
            st.divider()
            col1, col2 = st.columns(2)
            total_clients = len(df_display)
            vip_count = len(df_display[df_display["عدد الطلبات"].str.contains("🌟")])
            
            col1.metric("إجمالي العملاء", total_clients)
            col2.metric("عملاء VIP ✨", vip_count, delta="ولاء مرتفع", delta_color="normal")

        else:
            st.info("📭 لا يوجد عملاء مسجلين في النظام حالياً.")

    except Exception as e:
        st.error(f"❌ حدث خطأ أثناء تحميل بيانات العملاء: {e}")
