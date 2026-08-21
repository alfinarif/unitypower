import io
from django.http import FileResponse
from django.http import HttpResponse

# reportlab package import
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle




# Export invoice data excel and csv format
def export_invoice_data(model_object):
    data_object = model_object
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=40, leftMargin=40,
                            topMargin=90, bottomMargin=10)
    
    story = []
    styles = getSampleStyleSheet()
    
    # Modern Title Style
    title_style = ParagraphStyle(
        'ModernTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#1E293B')
    )
    
    story.append(Paragraph("#Invoices Reports", title_style))
    story.append(Spacer(1, 15))
    
    # Modern Table Design
    data = [
        [
            'Payment For', 
            'Payment Method',
            'Amounts',
            'Pay Month',
            'Status',
        ],

        [
            data_object.calculation_type,
            data_object.payment_method,
            f'TK{data_object.amount_of_money}',
            f'{data_object.pay_year} / {data_object.pay_month}',
            data_object.status,

        ],
    ]
    t = Table(data, colWidths=[120, 200, 90])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.HexColor('#CBD5E1')),
        ('LINEBELOW', (0, 1), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
    ]))
    story.append(t)
    
    def draw_decorations(canvas, document):
        canvas.saveState()
        canvas.setFillColor(colors.HexColor('#0EA5E9')) # Modern blue accent bar
        canvas.rect(0, letter[1] - 12, letter[0], 12, fill=1, stroke=0)
        canvas.restoreState()

    doc.build(story, onFirstPage=draw_decorations, onLaterPages=draw_decorations)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type="application/pdf")
    response['Content-Disposition'] = f"attachment; filename={data_object.invoice_number}_reports.pdf"

    return response





# Export invoice data excel and csv format
def export_unpaid_data_as_pdf():
    # data_object = model_object
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=40, leftMargin=40,
                            topMargin=90, bottomMargin=10)
    
    story = []
    styles = getSampleStyleSheet()
    
    # Modern Title Style
    title_style = ParagraphStyle(
        'ModernTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#1E293B')
    )
    
    story.append(Paragraph("#Invoices Reports", title_style))
    story.append(Spacer(1, 15))
    
    # Modern Table Design
    data = [
        [
            'Payment For', 
            'Payment Method',
            'Amounts',
            'Pay Month',
            'Status',
        ],

        [
            'Hello Alfin Arif',
            'Cash',
            'Amount',
            'Year/Month',
            'Unpaid',
            # data_object.calculation_type,
            # data_object.payment_method,
            # f'TK{data_object.amount_of_money}',
            # f'{data_object.pay_year} / {data_object.pay_month}',
            # data_object.status,

        ],
    ]
    t = Table(data, colWidths=[120, 200, 90])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.HexColor('#CBD5E1')),
        ('LINEBELOW', (0, 1), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
    ]))
    story.append(t)
    
    def draw_decorations(canvas, document):
        canvas.saveState()
        canvas.setFillColor(colors.HexColor('#0EA5E9')) # Modern blue accent bar
        canvas.rect(0, letter[1] - 12, letter[0], 12, fill=1, stroke=0)
        canvas.restoreState()

    doc.build(story, onFirstPage=draw_decorations, onLaterPages=draw_decorations)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type="application/pdf")
    response['Content-Disposition'] = f"attachment; filename=unpaid_reports.pdf"

    return response














