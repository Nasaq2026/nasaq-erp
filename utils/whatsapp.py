# utils/whatsapp.py
import webbrowser
import urllib.parse

def send_wa_template(phone, order_id, client_name, total, paid, template_type):
    rem = total - paid
    
    if template_type == "ready":
        msg = f"أهلاً بك أستاذ/ة {client_name} 🌹\n\nيسعدنا إبلاغك بأن طلبك رقم #{order_id} لدى *مؤسسة نسق* أصبح جاهزاً للاستلام الآن 😍.\n\nالمبلغ المتبقي: {rem} ر.س\n\nنسعد بزيارتك!"
    elif template_type == "processing":
        msg = f"مرحباً {client_name}،\nطلبك رقم #{order_id} حالياً قيد التنفيذ والطباعة 🖨️. سنقوم بإبلاغك فور الانتهاء.\nشكراً لثقتكم بمؤسسة نسق."
    elif template_type == "invoice":
        msg = f"مرحباً {client_name}،\nمرفق تفاصيل فاتورتك رقم #{order_id}:\nالإجمالي: {total} ر.س\nالمدفوع: {paid} ر.س\nالمتبقي: {rem} ر.س\nنسعد بخدمتكم."

    # استخدام رابط api.whatsapp.com لفتح المحادثة ونسخ النص تلقائياً
    safe_msg = urllib.parse.quote(msg)
    # تنظيف رقم الجوال (إضافة مفتاح السعودية إذا لم يكن موجوداً)
    clean_phone = phone.replace("+", "").replace(" ", "")
    if clean_phone.startswith("05"):
        clean_phone = "966" + clean_phone[1:]

    url = f"https://api.whatsapp.com/send?phone={clean_phone}&text={safe_msg}"
    webbrowser.open(url)