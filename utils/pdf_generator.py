from fpdf import FPDF
import datetime

class NasqInvoice(FPDF):
    def header(self):
        # إضافة شعار نَسق (تأكد من وجود ملف logo.png في مجلد assets)
        try:
            self.image('assets/logo.png', 10, 8, 33)
        except:
            self.set_font('Arial', 'B', 15)
            self.cell(0, 10, 'NASAQ ADVERTISING', 0, 1, 'L')
            
        self.set_font('Arial', 'B', 20)
        self.cell(0, 10, 'TAX INVOICE / فاتورة ضريبية', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()} | NASAQ ERP System - Jazan, KSA', 0, 0, 'C')

def generate_invoice_pdf(order_data, client_data):
    pdf = NasqInvoice()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # قسم بيانات الفاتورة
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(95, 10, f"Invoice No: #INV-{order_data['id']}", 1, 0, 'L', fill=True)
    pdf.cell(95, 10, f"Date: {datetime.datetime.now().strftime('%Y-%m-%d')}", 1, 1, 'L', fill=True)
    
    pdf.ln(5)

    # قسم بيانات العميل (التي أضفناها للسجل)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Client Information / بيانات العميل", 0, 1, 'R')
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 8, 
        f"Customer: {client_data['name']}\n"
        f"VAT Number: {client_data['vat']}\n"
        f"CR Number: {client_data['cr']}\n"
        f"Address: {client_data['address']}", 
        1, 'R')

    pdf.ln(10)

    # جدول المنتجات
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(100, 10, "Description / الوصف", 1)
    pdf.cell(30, 10, "Qty", 1)
    pdf.cell(30, 10, "Price", 1)
    pdf.cell(30, 10, "Total", 1, 1)

    pdf.set_font("Arial", size=10)
    pdf.cell(100, 10, order_data['project_name'], 1)
    pdf.cell(30, 10, "1", 1) # الكمية
    pdf.cell(30, 10, f"{order_data['price']}", 1)
    pdf.cell(30, 10, f"{order_data['price']}", 1, 1)

    # الحساب النهائي
    pdf.ln(5)
    pdf.cell(130, 10, "Subtotal (Excl. VAT)", 0, 0, 'R')
    pdf.cell(60, 10, f"{order_data['price']:.2f} SAR", 1, 1, 'C')
    
    pdf.cell(130, 10, "VAT (15%)", 0, 0, 'R')
    tax = float(order_data['price']) * 0.15
    pdf.cell(60, 10, f"{tax:.2f} SAR", 1, 1, 'C')

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(130, 10, "Total Amount Due", 0, 0, 'R')
    total = float(order_data['price']) + tax
    pdf.cell(60, 10, f"{total:,.2f} SAR", 1, 1, 'C', fill=True)

    return pdf.output(dest='S') # إرجاع الملف كـ Bytes
