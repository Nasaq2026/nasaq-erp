# utils/invoice.py
import os
import webbrowser
from datetime import datetime
from utils.zatca import generate_zatca_qr

def generate_invoice_html(row):
    # افتراض أن row يحتوي على البيانات من الداتابيز
    order_id, client, phone, date_in, date_out, price, vat, total, paid, cost, profit, designer, cat, details, status = row
    
    # توليد باركود هيئة الزكاة
    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    qr_base64 = generate_zatca_qr("مؤسسة نسق للدعاية والإعلان", "312345678900003", timestamp, total, vat)

    html = f"""
    <html dir="rtl"><body style="font-family:Tahoma, Arial; padding:40px; color:#333;">
    <div style="border: 2px solid #2980b9; padding: 20px; border-radius: 10px; max-width: 800px; margin: auto;">
        
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="text-align: right;">
                <h1 style="color:#2980b9; margin:0;">مؤسسة نسق للدعاية والإعلان</h1>
                <p>الرقم الضريبي: 312345678900003</p>
                <h3>فاتورة ضريبية مبسطة | Simplified Tax Invoice</h3>
                <p><b>رقم الفاتورة:</b> #{order_id}</p>
            </div>
            <div>
                <img src="data:image/png;base64,{qr_base64}" alt="ZATCA QR Code" />
            </div>
        </div>
        <hr style="border: 1px solid #2980b9;">
        
        <div style="display: flex; justify-content: space-between; margin-top:20px;">
            <div><p><b>العميل:</b> {client}</p><p><b>الجوال:</b> {phone}</p></div>
            <div><p><b>التاريخ:</b> {date_in}</p><p><b>المصمم:</b> {designer}</p></div>
        </div>
        
        <table border="1" style="width:100%; border-collapse:collapse; text-align:center; font-size:16px; margin-top:20px;">
            <tr style="background:#2980b9; color:white; height:40px;">
                <th>الوصف</th><th>المبلغ (غير شامل الضريبة)</th><th>الضريبة (15%)</th><th>الإجمالي شامل الضريبة</th>
            </tr>
            <tr style="height:50px;">
                <td>{cat}</td>
                <td>{price:.2f}</td>
                <td>{vat:.2f}</td>
                <td><b>{total:.2f}</b></td>
            </tr>
        </table>

        <table border="1" style="width:50%; border-collapse:collapse; text-align:center; font-size:16px; margin-top:20px; margin-right: auto;">
             <tr style="height:40px;">
                <td style="background:#f9f9f9;"><b>المدفوع</b></td><td>{paid:.2f} ر.س</td>
            </tr>
            <tr style="height:40px;">
                <td style="background:#f9f9f9;"><b>المتبقي</b></td><td style="color:red;"><b>{total - paid:.2f} ر.س</b></td>
            </tr>
        </table>
    </div>
    </body></html>"""
    
    with open("temp_inv.html", "w", encoding="utf-8") as f: 
        f.write(html)
    webbrowser.open("file://" + os.path.abspath("temp_inv.html"))