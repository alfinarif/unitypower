import os
from django.conf import settings
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from membership.models import User, Profile, Nominee
from finance.models import PaymentRequestModel



# Export member list PDF
def download_member_report(request):
    # Create the HTTP response with PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="member_report.pdf"'

    # Setup document
    doc = SimpleDocTemplate(response, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1a365d'),
        alignment=0,
        leading=3,
        spaceAfter=15
    )
    info_style = ParagraphStyle(
        'InfoStyle',
        parent=styles['Heading3'],
        fontSize=10,
        textColor=colors.HexColor('#1a365d'),
        alignment=0,
        leading=5,
        spaceAfter=5
    )
    cell_style = ParagraphStyle(
        'CellStyle',
        parent=styles['Normal'],
        fontSize=10,
        leading=12,
        textColor=colors.HexColor('#2d3748')
    )
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontSize=10,
        leading=12,
        textColor=colors.whitesmoke,
        fontName='Helvetica-Bold'
    )

    # FIX 1: Add Company Logo (Reduced height/width to prevent blocking page budget)
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'unity_power_logo.png')
    if os.path.exists(logo_path):
        # A 120x120 logo takes up massive real estate. 
        # Shrinking it ensures elements split across pages gracefully.
        logo = Image(logo_path, width=70, height=70)
        logo.hAlign = 'LEFT'
        story.append(logo)
        story.append(Spacer(1, 15))

    # Title
    story.append(Paragraph("Unity Power Association", title_style))
    story.append(Paragraph("Members List Reports", title_style))
    story.append(Paragraph("E-mail: info@unitypower.online", info_style))
    story.append(Paragraph("Phone: +966506897109", info_style))
    story.append(Paragraph("Address: Riyadh, Saudi Arabia", info_style))
    story.append(Spacer(1, 10))

    # Dynamic User Data
    member_list = User.objects.all().order_by('-id')

    # Table Header
    table_data = [[
        Paragraph("Email", header_style),
        Paragraph("A/C Number", header_style),
        Paragraph("Type", header_style),
        Paragraph("Is HR", header_style),
        Paragraph("Is Admin", header_style),
        Paragraph("Is Finance", header_style),
    ]]

    # Populate Table Rows dynamically
    for user in member_list:
        hr_status = "Yes" if user.is_hr else "No"
        admin_status = "Yes" if user.is_admin else "No"
        finance_status = "Yes" if user.is_finance else "No"
        
        # FIX 2: Handle None values cleanly inside Paragraphs to prevent rendering breaks
        email_txt = user.email if user.email else ""
        account_number = str(user.account_number) if user.account_number is not None else ""
        user_type = user.user_type if user.user_type else ""

        table_data.append([
            Paragraph(email_txt, cell_style),
            Paragraph(account_number, cell_style),
            Paragraph(user_type, cell_style),
            Paragraph(hr_status, cell_style),
            Paragraph(admin_status, cell_style),
            Paragraph(finance_status, cell_style),
        ])

    # Create Table with specific column widths (Total width: 532)
    column_widths = [180, 71, 71, 70, 70, 70] 
    
    # FIX 3: Explicitly set repeatRows=1 so headers replicate on multi-page breaks automatically
    user_table = Table(table_data, colWidths=column_widths, repeatRows=1)
    
    # Style the table
    # FIX 4: Replaced 'ROWBACKGROUNDS' with an explicit alternating background command loop.
    # The built-in list tuple for ROWBACKGROUNDS occasionally mismatches during infinite splits.
    t_style = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a365d')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e0'))
    ]
    
    # Add alternating backgrounds safely row-by-row
    for i in range(1, len(table_data)):
        if i % 2 == 0:
            t_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f7fafc')))
        else:
            t_style.append(('BACKGROUND', (0, i), (-1, i), colors.white))

    user_table.setStyle(TableStyle(t_style))
    story.append(user_table)

    # Build PDF
    doc.build(story)
    return response



# Export profile list PDF
def download_profile_report(request):
    # Create the HTTP response with PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="members_profile_report.pdf"'

    # Setup document
    doc = SimpleDocTemplate(response, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor("#033985"),
        alignment=0,
        leading=3,
        spaceAfter=20
    )
    info_style = ParagraphStyle(
        'InfoStyle',
        parent=styles['Heading3'],
        fontSize=10,
        textColor=colors.HexColor("#263f63"),
        alignment=0,
        leading=5,
        spaceAfter=10
    )
    cell_style = ParagraphStyle(
        'CellStyle',
        parent=styles['Normal'],
        fontSize=10,
        leading=12,
        textColor=colors.HexColor('#2d3748')
    )
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontSize=10,
        leading=12,
        textColor=colors.whitesmoke,
        fontName='Helvetica-Bold'
    )

    # FIX 1: Add Company Logo (Reduced height/width to prevent blocking page budget)
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'unity_power_logo.png')
    if os.path.exists(logo_path):
        # A 120x120 logo takes up massive real estate. 
        # Shrinking it ensures elements split across pages gracefully.
        logo = Image(logo_path, width=70, height=70)
        logo.hAlign = 'LEFT'
        story.append(logo)
        story.append(Spacer(1, 15))

    # Title
    story.append(Paragraph("Unity Power Association", title_style))
    story.append(Paragraph("Profiles List Reports", title_style))
    story.append(Paragraph("E-mail: info@unitypower.online", info_style))
    story.append(Paragraph("Phone: +966506897109", info_style))
    story.append(Paragraph("Address: Riyadh, Saudi Arabia", info_style))
    story.append(Spacer(1, 15))

    # Dynamic Profile Data
    profile_list = Profile.objects.all().order_by('-id')

    # Table Header
    table_data = [[
        Paragraph("Member", header_style),
        Paragraph("Name", header_style),
        Paragraph("Father Name", header_style),
        Paragraph("NID Number", header_style),
        Paragraph("Phone Number", header_style),
        Paragraph("Address", header_style),
    ]]

    # Populate Table Rows dynamically
    for profile in profile_list:
        # FIX 2: Handle None values cleanly inside Paragraphs to prevent rendering breaks
        member = profile.user.email if profile.user.email else "X"
        full_name = profile.full_name if profile.full_name else "X"
        father_name = profile.father_name if profile.father_name else "X"
        national_id = profile.national_id if profile.national_id else "X"
        phone_number = profile.phone_number if profile.phone_number else "X"
        village = profile.village if profile.village else "X"
        

        table_data.append([
            Paragraph(member, cell_style),
            Paragraph(full_name, cell_style),
            Paragraph(father_name, cell_style),
            Paragraph(national_id, cell_style),
            Paragraph(phone_number, cell_style),
            Paragraph(village, cell_style),
        ])

    # Create Table with specific column widths (Total width: 532)
    column_widths = [180, 71, 71, 70, 70, 70] 
    
    # FIX 3: Explicitly set repeatRows=1 so headers replicate on multi-page breaks automatically
    user_table = Table(table_data, colWidths=column_widths, repeatRows=1)
    
    # Style the table
    # FIX 4: Replaced 'ROWBACKGROUNDS' with an explicit alternating background command loop.
    # The built-in list tuple for ROWBACKGROUNDS occasionally mismatches during infinite splits.
    t_style = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a365d')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e0'))
    ]
    
    # Add alternating backgrounds safely row-by-row
    for i in range(1, len(table_data)):
        if i % 2 == 0:
            t_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f7fafc')))
        else:
            t_style.append(('BACKGROUND', (0, i), (-1, i), colors.white))

    user_table.setStyle(TableStyle(t_style))
    story.append(user_table)

    # Build PDF
    doc.build(story)
    return response



# Export nominee list PDF
def download_nominee_report(request):
    # Create the HTTP response with PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="members_nominee_report.pdf"'

    # Setup document
    doc = SimpleDocTemplate(response, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor("#033985"),
        alignment=0,
        leading=3,
        spaceAfter=20
    )
    info_style = ParagraphStyle(
        'InfoStyle',
        parent=styles['Heading3'],
        fontSize=10,
        textColor=colors.HexColor("#263f63"),
        alignment=0,
        leading=5,
        spaceAfter=10
    )
    cell_style = ParagraphStyle(
        'CellStyle',
        parent=styles['Normal'],
        fontSize=10,
        leading=12,
        textColor=colors.HexColor('#2d3748')
    )
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontSize=10,
        leading=12,
        textColor=colors.whitesmoke,
        fontName='Helvetica-Bold'
    )

    # FIX 1: Add Company Logo (Reduced height/width to prevent blocking page budget)
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'unity_power_logo.png')
    if os.path.exists(logo_path):
        # A 120x120 logo takes up massive real estate. 
        # Shrinking it ensures elements split across pages gracefully.
        logo = Image(logo_path, width=70, height=70)
        logo.hAlign = 'LEFT'
        story.append(logo)
        story.append(Spacer(1, 15))

    # Title
    story.append(Paragraph("Unity Power Association", title_style))
    story.append(Paragraph("Nominee List Reports", title_style))
    story.append(Paragraph("E-mail: info@unitypower.online", info_style))
    story.append(Paragraph("Phone: +966506897109", info_style))
    story.append(Paragraph("Address: Riyadh, Saudi Arabia", info_style))
    story.append(Spacer(1, 15))

    # Dynamic Profile Data
    nominee_list = Nominee.objects.all().order_by('-id')

    # Table Header
    table_data = [[
        Paragraph("Member", header_style),
        Paragraph("Nominee Name", header_style),
        Paragraph("Relation", header_style),
        Paragraph("Phone Number", header_style),
        Paragraph("Address", header_style),
    ]]

    # Populate Table Rows dynamically
    for nominee in nominee_list:
        # FIX 2: Handle None values cleanly inside Paragraphs to prevent rendering breaks
        member = nominee.profile.user.email if nominee.profile.user.email else "X"
        full_name = nominee.full_name if nominee.full_name else "X"
        relation = nominee.relation if nominee.relation else "X"
        phone_number = nominee.phone_number if nominee.phone_number else "X"
        address = nominee.address if nominee.address else "X"
        

        table_data.append([
            Paragraph(member, cell_style),
            Paragraph(full_name, cell_style),
            Paragraph(relation, cell_style),
            Paragraph(phone_number, cell_style),
            Paragraph(address, cell_style),
        ])

    # Create Table with specific column widths (Total width: 532)
    column_widths = [180, 88, 88, 88, 88]
    
    # FIX 3: Explicitly set repeatRows=1 so headers replicate on multi-page breaks automatically
    user_table = Table(table_data, colWidths=column_widths, repeatRows=1)
    
    # Style the table
    # FIX 4: Replaced 'ROWBACKGROUNDS' with an explicit alternating background command loop.
    # The built-in list tuple for ROWBACKGROUNDS occasionally mismatches during infinite splits.
    t_style = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a365d')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e0'))
    ]
    
    # Add alternating backgrounds safely row-by-row
    for i in range(1, len(table_data)):
        if i % 2 == 0:
            t_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f7fafc')))
        else:
            t_style.append(('BACKGROUND', (0, i), (-1, i), colors.white))

    user_table.setStyle(TableStyle(t_style))
    story.append(user_table)

    # Build PDF
    doc.build(story)
    return response




# Export single transaction invoice PDF
def download_invoice_report(id):
    # Create the HTTP response with PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="members_nominee_report.pdf"'

    # Setup document
    doc = SimpleDocTemplate(response, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor("#033985"),
        alignment=0,
        leading=3,
        spaceAfter=20
    )
    info_style = ParagraphStyle(
        'InfoStyle',
        parent=styles['Heading3'],
        fontSize=10,
        textColor=colors.HexColor("#263f63"),
        alignment=0,
        leading=5,
        spaceAfter=10
    )
    cell_style = ParagraphStyle(
        'CellStyle',
        parent=styles['Normal'],
        fontSize=10,
        leading=12,
        textColor=colors.HexColor('#2d3748')
    )
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontSize=10,
        leading=12,
        textColor=colors.whitesmoke,
        fontName='Helvetica-Bold'
    )

    # FIX 1: Add Company Logo (Reduced height/width to prevent blocking page budget)
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'unity_power_logo.png')
    if os.path.exists(logo_path):
        # A 120x120 logo takes up massive real estate. 
        # Shrinking it ensures elements split across pages gracefully.
        logo = Image(logo_path, width=70, height=70)
        logo.hAlign = 'LEFT'
        story.append(logo)
        story.append(Spacer(1, 15))

    # Title
    story.append(Paragraph("Unity Power Finance Department", title_style))
    story.append(Paragraph("Invoice Reports", title_style))
    story.append(Paragraph("E-mail: info@unitypower.online", info_style))
    story.append(Paragraph("Phone: +966506897109", info_style))
    story.append(Paragraph("Address: Riyadh, Saudi Arabia", info_style))
    story.append(Spacer(1, 15))

    # Dynamic Profile Data
    invoice = PaymentRequestModel.objects.get(id=id)

    # Table Header
    table_data = [[
        Paragraph("Payment Type", header_style),
        Paragraph("Payment Method", header_style),
        Paragraph("Amount", header_style),
        Paragraph("Date", header_style),
        Paragraph("Progress Status", header_style),
    ]]

    # Populate Table Rows dynamically
    calculation_type = invoice.calculation_type if invoice.calculation_type else "X"
    payment_method = invoice.payment_method if invoice.payment_method else "X"
    amount_of_money = invoice.amount_of_money if invoice.amount_of_money else "X"
    status = invoice.status if invoice.status else "X"

    pay_date = f'{invoice.pay_year} / {invoice.pay_month}'


    table_data.append([
        Paragraph(calculation_type, cell_style),
        Paragraph(payment_method, cell_style),
        Paragraph(str(amount_of_money), cell_style),
        Paragraph(pay_date, cell_style),
        Paragraph(status, cell_style),
    ])

    # Create Table with specific column widths (Total width: 532)
    column_widths = [180, 88, 88, 88, 88]
    
    # FIX 3: Explicitly set repeatRows=1 so headers replicate on multi-page breaks automatically
    user_table = Table(table_data, colWidths=column_widths, repeatRows=1)
    
    # Style the table
    # FIX 4: Replaced 'ROWBACKGROUNDS' with an explicit alternating background command loop.
    # The built-in list tuple for ROWBACKGROUNDS occasionally mismatches during infinite splits.
    t_style = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a365d')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e0'))
    ]
    
    # Add alternating backgrounds safely row-by-row
    for i in range(1, len(table_data)):
        if i % 2 == 0:
            t_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f7fafc')))
        else:
            t_style.append(('BACKGROUND', (0, i), (-1, i), colors.white))

    user_table.setStyle(TableStyle(t_style))
    story.append(user_table)

    # Build PDF
    doc.build(story)
    return response










