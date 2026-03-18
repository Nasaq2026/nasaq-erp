# utils/work_order.py
from datetime import datetime

def generate_work_order_html(row):
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
        .wo-card {{ border: 2px solid #27ae60; padding: 25px; max-width: 800px; margin: auto; border-radius: 12px; }}
        .wo-header {{ color: #27ae60; text-align: center; font-size: 26px; font-weight: bold; border-bottom: 2px solid #27ae60; padding-bottom: 10px; }}
        .tech-info {{ background: #f8f9fa; border: 1px solid #ddd; padding: 20px; margin-top: 20px; border-radius: 8px; line-height: 1.8; }}
        .team-table {{ width: 100%; border-collapse: collapse; margin-top: 25px; }}
        .team-table th {{ background: #27ae60; color: white; padding: 12px; border: 1px solid #ddd; }}
        .team-table td {{ padding: 20px; border: 1px solid #ddd; text-align: center; font-size: 14px; }}
        .footer-sig {{ margin-top: 25px; border: 1px dashed #27ae60; padding: 20px; border-radius: 8px; }}
    </style>
    </head>
    <body onload="window.print()">
        <div class="wo-card">
            <div class="wo-header">أمر تشغيل / عمل (Work Order)</div>
            <div style="display: flex; justify-content: space-between; margin-top: 15px; font-weight: bold;">
                <span>تاريخ الإصدار: {datetime.now().strftime('%Y-%m-%d')}</span>
                <span>رقم أمر العمل: {sn}</span>
            </div>

            <div class="tech-info">
                <h3 style="color:#27ae60; margin-top:0; border-bottom: 1px solid #eee;">🛠️ التفاصيل الفنية للعمل:</h3>
                <p><b>القسم / الخدمة:</b> {category}</p>
                <p><b>ملاحظات التنفيذ:</b> {details}</p>
                <p style="color:#e67e22; font-weight:bold;">🚨 الحالة: قيد التنفيذ بالورشة</p>
            </div>

            <table class="team-table">
                <tr><th>المصمم</th><th>فني الطباعة/القص</th><th>فني التركيب</th></tr>
                <tr>
                    <td>{designer}<br><br><span style="color:#ccc;">التوقيع: .................</span></td>
                    <td>أحمد (فني طباعة)<br><br><span style="color:#ccc;">التوقيع: .................</span></td>
                    <td>سيد (فني تركيب)<br><br><span style="color:#ccc;">التوقيع: .................</span></td>
                </tr>
            </table>

            <div class="footer-sig">
                <h4 style="margin:0; color:#27ae60;">🤝 إقرار استلام العميل:</h4>
                <p>العميل: <b>{client}</b> | الجوال: <b>{phone}</b></p>
                <p style="font-size: 13px;">أقر أنا العميل الموضح أعلاه باستلام العمل المطلوب بحالة ممتازة وحسب المواصفات المتفق عليها.</p>
                <br>
                <p style="text-align: left;">توقيع العميل: ........................................</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html
