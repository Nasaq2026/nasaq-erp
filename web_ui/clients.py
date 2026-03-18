# web_ui/clients.py
import streamlit as st
import pandas as pd

def render_clients(conn):
    st.title("👥 إدارة العملاء (CRM)")
    st.info("عرض قائمة العملاء، بياناتهم الضريبية، ومتابعة مستوى الولاء (العملاء المميزين).")

    try:
        conn.rollback()
        cursor = conn.cursor()

        # 1. سحب البيانات بنفس ترتيب الديسكتوب
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
            # 2. إضافة لمسة الـ VIP الذكية (النجمة الذهبية 🌟)
            # بنطبقها على عمود "عدد الطلبات" زي ما عملت في الديسكتوب
            def apply_vip_status(row):
                count = row["عدد الطلبات"]
                if count >= 3:
                    return f"{count} 🌟"
                return str(count)

            df["عدد الطلبات"] = df.apply(apply_vip_status, axis=1)

            # 3. عرض الجدول بتنسيق ويب متجاوب
            st.dataframe(
                df, 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "رقم الجوال": st.column_config.TextColumn("رقم الجوال"),
                    "عدد الطلبات": st.column_config.TextColumn("عدد الطلبات", help="العملاء الذين لديهم 3 طلبات أو أكثر يحصلون على وسم VIP 🌟")
                }
            )

            # 4. إحصائية سريعة أسفل الجدول
            st.divider()
            col1, col2 = st.columns(2)
            total_clients = len(df)
            vip_count = len(df[df["عدد الطلبات"].str.contains("🌟")])
            
            col1.metric("إجمالي العملاء", total_clients)
            col2.metric("عملاء VIP ✨", vip_count, delta="ولاء مرتفع", delta_color="normal")

        else:
            st.warning("لا يوجد عملاء مسجلين في النظام حالياً.")

    except Exception as e:
        st.error(f"حدث خطأ أثناء تحميل بيانات العملاء: {e}")