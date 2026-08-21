import io
import os
from django.conf import settings
from django.http import FileResponse
from django.views import View

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
# Added 'Image' to the platypus imports
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch







def download_member_list_pdf(request):
    
    # 1. Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # 2. Setup document geometry
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.5 * inch,
        leftMargin=0.5 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch
    )

    # 3. Initialize styles
    styles = getSampleStyleSheet()
    
    PRIMARY_COLOR = colors.HexColor("#1A365D")   # Deep navy blue
    SECONDARY_COLOR = colors.HexColor("#4A5568") # Slate grey
    LIGHT_BG = colors.HexColor("#F7FAFC")        # Off-white row background
    TEXT_DARK = colors.HexColor("#2D3748")       # Charcoal text

    title_style = ParagraphStyle(
        'InvoiceTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=PRIMARY_COLOR,
        alignment=2 # Right aligned
    )
    
    meta_label_style = ParagraphStyle(
        'MetaLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=SECONDARY_COLOR
    )
    
    meta_value_style = ParagraphStyle(
        'MetaValue',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=TEXT_DARK
    )

    cell_text_style = ParagraphStyle(
        'CellText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=TEXT_DARK
    )

    cell_header_style = ParagraphStyle(
        'CellHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.white
    )

    story = []

    # --- LOGO & HEADER SECTION ---
    company_info = "<font size=14><b>Unity Power</b></font><br/>info@unitypower.online<br/>+966506897109<br/>Riyadh, Saudi Arabia"
    
    # Resolve the static path to your logo image securely
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'unity_power_logo.png')
    
    # Fallback check so your app doesn't crash if the image file is physically missing
    if os.path.exists(logo_path):
        # Explicitly define width and height to keep the layout crisp (e.g., 1.5 inches wide)
        logo_img = Image(logo_path, width=1.5 * inch, height=1.5 * inch)
        # Center or left-align the logo inside its structural space
        logo_img.hAlign = 'LEFT'
        
        # Combine image and textual company details into one structural block
        logo_and_text = [logo_img, Spacer(1, 0.1 * inch), Paragraph(company_info, meta_value_style)]
    else:
        # Fallback if image asset does not exist yet
        logo_and_text = Paragraph(company_info, meta_value_style)

    header_data = [
        [logo_and_text, Paragraph("INVOICE", title_style)]
    ]
    
    header_table = Table(header_data, colWidths=[4.0 * inch, 3.5 * inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.4 * inch))

    # --- METADATA SECTION ---
    customer_info = "<b>Bill To:</b><br/>Finance Department<br/>Assistant Cashier: Foysal Ahammed<br/>foysal@gmail.com<br/>Riyadh, Saudi Arabia"
    invoice_details = "<b>Invoice #:</b> INV-2026-001<br/><b>Date:</b> August 15, 2026<br/><b>Due Date:</b> September 15, 2026<br/>"

    meta_data = [
        [Paragraph(customer_info, meta_value_style), Paragraph(invoice_details, meta_value_style)]
    ]
    meta_table = Table(meta_data, colWidths=[4.0 * inch, 3.5 * inch])
    meta_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 0.4 * inch))

    # --- Table Headers 
    table_data = [[
        Paragraph("Email Address", cell_header_style),
        Paragraph("Member Number", cell_header_style),
        Paragraph("Member Type", cell_header_style),
        Paragraph("Is HR", cell_header_style),
        Paragraph("Is Admin", cell_header_style),
        Paragraph("Is Finance", cell_header_style),
    ]]


    # --- LINE ITEMS TABLE ---
    items_raw_data = [
        ("alfin@gmail.com", "15", "Member", "True", "True", "True"),
        ("alfin@gmail.com", "15", "Member", "True", "True", "True"),
        ("alfin@gmail.com", "15", "Member", "True", "True", "True"),
        ("alfin@gmail.com", "15", "Member", "True", "True", "True"),
        ("alfin@gmail.com", "15", "Member", "True", "True", "True"),
    ]

    

    subtotal = 0
    # for desc, qty, price, email, hr, admin in items_raw_data:
    #     amount = qty * price
    #     subtotal += amount
    #     table_data.append([
    #         Paragraph(desc, cell_text_style),
    #         Paragraph(str(qty), cell_text_style),
    #         Paragraph(f"${price:,.2f}", cell_text_style),
    #         Paragraph(f"${amount:,.2f}", cell_text_style)
    #     ])

    vat_amount = subtotal * 0.15
    total_amount = subtotal + vat_amount

    table_data.append([Paragraph("", cell_text_style), Paragraph("", cell_text_style), Paragraph("Subtotal:", meta_label_style), Paragraph(f"${subtotal:,.2f}", cell_text_style)])
    table_data.append([Paragraph("", cell_text_style), Paragraph("", cell_text_style), Paragraph("VAT (15%):", meta_label_style), Paragraph(f"${vat_amount:,.2f}", cell_text_style)])
    table_data.append([Paragraph("", cell_text_style), Paragraph("", cell_text_style), Paragraph("Total Due:", meta_label_style), Paragraph(f"${total_amount:,.2f}", meta_label_style)])

    item_table = Table(table_data, colWidths=[4.0 * inch, 0.8 * inch, 1.3 * inch, 1.4 * inch])
    
    t_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY_COLOR),
        ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ])

    for i in range(len(items_raw_data)):
        if i % 2 == 0:
            t_style.add('BACKGROUND', (0, i), (-1, i), LIGHT_BG)
        t_style.add('LINEBELOW', (0, i), (-1, i), 0.5, colors.HexColor("#E2E8F0"))

    num_items = len(items_raw_data)
    t_style.add('LINEABOVE', (2, num_items + 1), (3, num_items + 1), 1, PRIMARY_COLOR)
    t_style.add('BACKGROUND', (2, num_items + 3), (3, num_items + 3), LIGHT_BG)

    item_table.setStyle(t_style)
    story.append(item_table)
    story.append(Spacer(1, 0.6 * inch))
    
    # --- FOOTER / TERMS ---
    terms_text = "<b>Terms & Conditions:</b><br/>Payment is due within 30 days. Transfer to Bank Account SA03 0000 0000 1234 5678. Thank you!"
    story.append(Paragraph(terms_text, meta_value_style))

    # 4. Build the document
    doc.build(story)

    # 5. FileResponse Download Settings
    buffer.seek(0)
    
    # CRITICAL CHANGES FOR DOWNLOAD:
    # Changed 'as_attachment' to True to force the browser to trigger a local file download interface.
    return FileResponse(
        buffer, 
        as_attachment=True, 
        filename='invoice_INV-2026-001.pdf',
        content_type='application/pdf'
    )