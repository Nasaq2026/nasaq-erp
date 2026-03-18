# utils/work_order.py
import os
import webbrowser
from datetime import datetime

def generate_work_order_html(order_row):
    # استخراج بيانات الطلب حسب ترتيب قاعدة البيانات الجديدة
    wo_sn = order_row[1]
    client_name = order_row[2]
    phone = order_row[3]
    cat = order_row[12]
    details = order_row[13]
    designer = order_row[14]
    tech = order_row[15]
    installer = order_row[16]
    req_install = "نعم (يوجد تركيب)" if order_row[17] else "لا (تسليم فقط)"
    notes = order_row[19]
    mat_type = order_row[20]
    dims = order_row[21]

    html = f"""
    <html dir="rtl"><body style="font-family:Tahoma, Arial; padding:40px; color:#333; line-height: 1.6;">
    <div style="border: 2px solid #10B981; padding: 20px; border-radius: 10px; max-width: 800px; margin: auto;">
        
        <h2 style="color:#10B981; text-align:center; border-bottom: 2px solid #10B981; padding-bottom:10px;">أمر تشغيل / عمل (Work Order)</h2>
        
        <table style="width:100%; margin-bottom:20px;">
            <tr>
                <td><b>رقم الأمر:</b> {wo_sn}</td>
                <td style="text-align:left;"><b>تاريخ الإصدار:</b> {datetime.now().strftime('%Y-%m-%d')}</td>
            </tr>
        </table>

        <div style="background:#f9f9f9; padding:15px; border-radius:8px; margin-bottom:20px; border: 1px solid #ddd;">
            <h3 style="margin-top:0; color:#2980b9;">🛠️ التفاصيل الفنية للعمل:</h3>
            <p><b>القسم/الخدمة:</b> {cat}</p>
            <p><b>الخامة المطلوبة:</b> {mat_type} &nbsp;&nbsp;|&nbsp;&nbsp; <b>المقاسات:</b> {dims}</p>
            <p><b>التفاصيل:</b><br>{details.replace(chr(10), '<br>')}</p>
            <p><b>ملاحظات للتنفيذ:</b> {notes}</p>
            <p><b>التركيب الخارجي:</b> <span style="color:red; font-weight:bold;">{req_install}</span></p>
        </div>

        <table border="1" style="width:100%; border-collapse:collapse; text-align:center; margin-bottom:20px;">
            <tr style="background:#10B981; color:white;">
                <th style="padding:10px;">المصمم</th><th style="padding:10px;">فني الطباعة/القص</th><th style="padding:10px;">فني التركيب</th>
            </tr>
            <tr>
                <td style="padding:15px;"><b>{designer}</b><br><br><br>التوقيع: ....................</td>
                <td style="padding:15px;"><b>{tech}</b><br><br><br>التوقيع: ....................</td>
                <td style="padding:15px;"><b>{installer}</b><br><br><br>التوقيع: ....................</td>
            </tr>
        </table>

        <div style="border: 1px dashed #7f8c8d; padding:15px; border-radius:8px; background-color:#f8f9fa;">
            <h3 style="margin-top:0;">🤝 إقرار استلام العميل:</h3>
            <p><b>العميل:</b> {client_name} &nbsp;&nbsp;|&nbsp;&nbsp; <b>الجوال:</b> {phone}</p>
            <p>أقر أنا العميل الموضح أعلاه باستلام العمل المطلوب بحالة ممتازة وحسب المواصفات المتفق عليها.</p>
            <br>
            <p><b>توقيع العميل:</b> ........................................</p>
        </div>
        
    </div>
    </body></html>
    """
    with open("temp_wo.html", "w", encoding="utf-8") as f:
        f.write(html)
    webbrowser.open("file://" + os.path.abspath("temp_wo.html"))