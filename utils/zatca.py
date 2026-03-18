# utils/zatca.py
import base64
import qrcode
import io

def generate_zatca_qr(seller_name, vat_number, timestamp, total_with_vat, vat_amount):
    def get_tlv(tag, value):
        val_bytes = str(value).encode('utf-8')
        return bytes([tag, len(val_bytes)]) + val_bytes

    tlv_data = b''
    tlv_data += get_tlv(1, seller_name)       # 1. اسم المورد
    tlv_data += get_tlv(2, vat_number)        # 2. الرقم الضريبي
    tlv_data += get_tlv(3, timestamp)         # 3. وقت وتاريخ الفاتورة
    tlv_data += get_tlv(4, total_with_vat)    # 4. إجمالي الفاتورة مع الضريبة
    tlv_data += get_tlv(5, vat_amount)        # 5. إجمالي الضريبة

    # تشفير البيانات بـ Base64
    base64_qr = base64.b64encode(tlv_data).decode('utf-8')

    # توليد صورة الباركود وتحويلها لنص ليتم دمجها في الـ HTML مباشرة
    qr = qrcode.QRCode(version=1, box_size=4, border=1)
    qr.add_data(base64_qr)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str