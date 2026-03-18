# utils/work_order.py
import streamlit as st
from datetime import datetime

def generate_work_order_html(row):
    # تفكيك بيانات الصف (id, sn, client, phone, date, stage, price, vat, total, paid, cost, profit, designer, cat, details)
    sn = row[1]
    client = row[2]
    phone = row[3]
    designer = row[12]
    category = row[13]
    details = row[14]

    html = f"""
    <html dir="rtl">
    <head><meta charset="UTF-8">
    <style>
        body {{ font-family: 'Arial', sans-serif; padding: 15px; }}
        .wo-card {{ border: 2px solid #27ae60; padding: 20px; max-width: 800px; margin: auto; border-radius: 8px; }}
        .wo-header {{ color: #27ae60; text-align: center; font-size: 24px; font-weight: bold; border-bottom: 2px solid #27ae60; padding-bottom: 10px; }}
        .tech-info {{ background: #f8f9fa; border: 1px solid #ddd; padding: 15px; margin-top: 20px; border-radius: 5px; }}
        .team-table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        .team-table th {{ background: #27ae60; color: white; padding: 10px; border: 1px solid #ddd; }}
        .team-table td {{ padding: 15px; border: 1px solid #ddd; text-align: center; font-size: 13px; }}
    </style>
    </head>
    <body>
        <div class="wo-card">
            <div class="wo-header">أمر تشغيل / عمل (Work Order)</div>
            <div style="display: flex; justify-content: space-between; margin-top: 10px;">
                <span>تاريخ الإصدار: {datetime.now().strftime('%Y-%m-%d')}</span>
                <span>رقم الأمر: {sn}</span>
            </div>

            <div class="tech-info">
                <h3 style="color:#27ae60; margin-top:0;">🛠️ التفاصيل الفنية للعمل:</h3>
                <p><b>القسم / الخدمة:</b> {category}</p>
                <p><b>ملاحظات التنفيذ:</b> {details}</p>
                <p style="color:red;"><b>التركيب الخارجي:</b> نعم (يوجد تركيب)</p>
            </div>

            <table class="team-table">
                <tr><th>المصمم</th><th>فني الطباعة/القص</th><th>فني التركيب</th></tr>
                <tr>
                    <td>{designer}<br><br>التوقيع: .................</td>
                    <td>أحمد (فني طباعة)<br><br>التوقيع: .................</td>
                    <td>سيد (فني تركيب)<br><br>التوقيع: .................</td>
                </tr>
            </table>

            <div style="margin-top: 20px; border: 1px dashed #27ae60; padding: 15px; border-radius: 5px;">
                <h4 style="margin:0;">🤝 إقرار استلام العميل:</h4>
                <p>العميل: {client} | الجوال: {phone}</p>
                <p style="font-size: 13px;">أقر أنا العميل الموضح أعلاه باستلام العمل المطلوب بحالة ممتازة وحسب المواصفات.</p>
                <p style="text-align: left;">توقيع العميل: ...........................</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html
