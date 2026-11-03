import os
from xml.sax.saxutils import escape

from django.conf import settings
from django.http import HttpResponse

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
)

from administration.helpers.paid_unpaid_billings import calculate_all_users_billing
from membership.models import User, Profile, Nominee
from finance.models import PaymentModel


# ---------------------------------------------------------------------------
# Shared Unity Power PDF theme
# ---------------------------------------------------------------------------

NAVY = colors.HexColor("#142B4A")
BLUE = colors.HexColor("#245B8F")
TEAL = colors.HexColor("#16A6A1")
INK = colors.HexColor("#263445")
MUTED = colors.HexColor("#68788A")
BORDER = colors.HexColor("#DCE4EC")
PALE = colors.HexColor("#F3F7FB")
WHITE = colors.white

PAGE_SIZE = landscape(letter)
PAGE_LEFT = 34
PAGE_RIGHT = 34
PAGE_TOP = 92
PAGE_BOTTOM = 48


def _pdf_styles():
    """Return consistent typography for all report PDFs."""
    base = getSampleStyleSheet()

    return {
        "report_title": ParagraphStyle(
            "UnityReportTitle",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=19,
            leading=23,
            textColor=NAVY,
            alignment=TA_LEFT,
            spaceAfter=3,
        ),
        "department": ParagraphStyle(
            "UnityDepartment",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            textColor=TEAL,
            alignment=TA_LEFT,
            spaceAfter=4,
        ),
        "contact": ParagraphStyle(
            "UnityContact",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=11,
            textColor=MUTED,
            alignment=TA_LEFT,
        ),
        "table_header": ParagraphStyle(
            "UnityTableHeader",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            textColor=WHITE,
            alignment=TA_LEFT,
            wordWrap="CJK",
        ),
        "table_cell": ParagraphStyle(
            "UnityTableCell",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            textColor=INK,
            alignment=TA_LEFT,
            wordWrap="CJK",
        ),
        "table_cell_small": ParagraphStyle(
            "UnityTableCellSmall",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=7.3,
            leading=9,
            textColor=INK,
            alignment=TA_LEFT,
            wordWrap="CJK",
        ),
        "empty": ParagraphStyle(
            "UnityEmpty",
            parent=base["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=9,
            leading=12,
            textColor=MUTED,
            alignment=TA_CENTER,
        ),
    }


def _safe_text(value, fallback=""):
    """Escape dynamic values so characters such as &, < and > render safely."""
    if value is None:
        value = fallback
    return escape(str(value))


def _paragraph(value, style, fallback=""):
    return Paragraph(_safe_text(value, fallback), style)


def _make_report_table(headers, rows, available_width, proportions=None, compact=False):
    """Create a polished, repeating-header table that can split across pages."""
    styles = _pdf_styles()
    header_style = styles["table_header"]
    cell_style = styles["table_cell_small"] if compact else styles["table_cell"]

    if not rows:
        return Table(
            [[Paragraph("No records found.", styles["empty"])]],
            colWidths=[available_width],
            style=TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), PALE),
                ("BOX", (0, 0), (-1, -1), 0.6, BORDER),
                ("TOPPADDING", (0, 0), (-1, -1), 16),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 16),
            ]),
        )

    if proportions is None:
        proportions = [1] * len(headers)

    total = float(sum(proportions))
    widths = [available_width * (part / total) for part in proportions]

    data = [[_paragraph(label, header_style) for label in headers]]
    for row in rows:
        data.append([
            value if isinstance(value, Paragraph) else _paragraph(value, cell_style)
            for value in row
        ])

    table = Table(
        data,
        colWidths=widths,
        repeatRows=1,
        hAlign="LEFT",
        splitByRow=1,
    )

    commands = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, 0), 11),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 11),
        ("TOPPADDING", (0, 1), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 8),
        ("LINEBELOW", (0, 0), (-1, 0), 1.2, TEAL),
        ("LINEBELOW", (0, 1), (-1, -1), 0.35, BORDER),
        ("LINEBEFORE", (1, 0), (-1, -1), 0.25, BORDER),
        ("BOX", (0, 0), (-1, -1), 0.55, BORDER),
    ]

    for row_index in range(1, len(data)):
        if row_index % 2 == 0:
            commands.append(("BACKGROUND", (0, row_index), (-1, row_index), PALE))
        else:
            commands.append(("BACKGROUND", (0, row_index), (-1, row_index), WHITE))

    table.setStyle(TableStyle(commands))
    return table


def _draw_page_chrome(canvas, doc):
    """Draw the brand header and page footer on every page."""
    canvas.saveState()
    page_width, page_height = PAGE_SIZE

    # Slim brand strip
    canvas.setFillColor(NAVY)
    canvas.rect(0, page_height - 8, page_width, 8, fill=1, stroke=0)
    canvas.setFillColor(TEAL)
    canvas.rect(0, page_height - 8, page_width * 0.23, 8, fill=1, stroke=0)

    # Logo (optional)
    logo_path = os.path.join(
        settings.BASE_DIR, "static", "images", "unity_power_logo.png"
    )
    logo_x = PAGE_LEFT
    logo_y = page_height - 77
    logo_drawn = False

    if os.path.exists(logo_path):
        try:
            logo = Image(logo_path, width=55, height=55)
            logo.drawOn(canvas, logo_x, logo_y)
            logo_drawn = True
        except Exception:
            # A missing/invalid logo should not prevent report generation.
            logo_drawn = False

    text_x = PAGE_LEFT + (68 if logo_drawn else 0)

    canvas.setFillColor(NAVY)
    canvas.setFont("Helvetica-Bold", 15)
    canvas.drawString(text_x, page_height - 39, "UNITY POWER ASSOCIATION")

    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(
        text_x, page_height - 54,
        "info@unitypower.online  |  +966506897109  |  Riyadh, Saudi Arabia"
    )

    # Header divider
    canvas.setStrokeColor(BORDER)
    canvas.setLineWidth(0.7)
    canvas.line(PAGE_LEFT, page_height - 84, page_width - PAGE_RIGHT, page_height - 84)

    # Footer
    canvas.setStrokeColor(BORDER)
    canvas.line(PAGE_LEFT, 34, page_width - PAGE_RIGHT, 34)
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(PAGE_LEFT, 21, "Unity Power Association  |  Official Report")
    canvas.drawRightString(
        page_width - PAGE_RIGHT, 21, f"Page {doc.page}"
    )
    canvas.restoreState()


def _create_pdf_response(filename):
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


def _build_report(response, report_title, table, department=None):
    """Build every report with the same page geometry and page furniture."""
    doc = SimpleDocTemplate(
        response,
        pagesize=PAGE_SIZE,
        rightMargin=PAGE_RIGHT,
        leftMargin=PAGE_LEFT,
        topMargin=PAGE_TOP,
        bottomMargin=PAGE_BOTTOM,
        title=report_title,
        author="Unity Power Association",
        subject=report_title,
        pageCompression=1,
    )

    styles = _pdf_styles()
    story = []

    if department:
        story.append(Paragraph(_safe_text(department), styles["department"]))

    story.append(Paragraph(_safe_text(report_title), styles["report_title"]))
    story.append(Spacer(1, 13))
    story.append(table)

    doc.build(
        story,
        onFirstPage=_draw_page_chrome,
        onLaterPages=_draw_page_chrome,
    )
    return response


# ---------------------------------------------------------------------------
# Export member list PDF
# ---------------------------------------------------------------------------

def download_member_report(request):
    response = _create_pdf_response("member_report.pdf")

    member_list = User.objects.all().order_by("-id")
    rows = []

    for user in member_list:
        hr_status = "Yes" if user.is_hr else "No"
        admin_status = "Yes" if user.is_admin else "No"
        finance_status = "Yes" if user.is_finance else "No"

        email_txt = user.email if user.email else ""
        account_number = str(user.account_number) if user.account_number is not None else ""
        user_type = user.user_type if user.user_type else ""

        rows.append([
            email_txt,
            account_number,
            user_type,
            hr_status,
            admin_status,
            finance_status,
        ])

    table = _make_report_table(
        ["Email", "A/C Number", "Type", "Is HR", "Is Admin", "Is Finance"],
        rows,
        PAGE_SIZE[0] - PAGE_LEFT - PAGE_RIGHT,
        proportions=[2.7, 1.0, 1.0, 0.8, 0.9, 1.0],
    )
    return _build_report(response, "Members List Reports", table)


# ---------------------------------------------------------------------------
# Export profile list PDF
# ---------------------------------------------------------------------------

def download_profile_report(request):
    response = _create_pdf_response("members_profile_report.pdf")

    profile_list = Profile.objects.all().order_by("-id")
    rows = []

    for profile in profile_list:
        member = profile.user.email if profile.user.email else "X"
        full_name = profile.full_name if profile.full_name else "X"
        father_name = profile.father_name if profile.father_name else "X"
        national_id = profile.national_id if profile.national_id else "X"
        phone_number = profile.phone_number if profile.phone_number else "X"
        village = profile.village if profile.village else "X"

        rows.append([
            member,
            full_name,
            father_name,
            national_id,
            phone_number,
            village,
        ])

    table = _make_report_table(
        ["Member", "Name", "Father Name", "NID Number", "Phone Number", "Address"],
        rows,
        PAGE_SIZE[0] - PAGE_LEFT - PAGE_RIGHT,
        proportions=[1.8, 1.35, 1.35, 1.25, 1.25, 1.6],
    )
    return _build_report(response, "Profiles List Reports", table)


# ---------------------------------------------------------------------------
# Export nominee list PDF
# ---------------------------------------------------------------------------

def download_nominee_report(request):
    response = _create_pdf_response("members_nominee_report.pdf")

    nominee_list = Nominee.objects.all().order_by("-id")
    rows = []

    for nominee in nominee_list:
        member = nominee.profile.user.email if nominee.profile.user.email else "X"
        full_name = nominee.full_name if nominee.full_name else "X"
        relation = nominee.relation if nominee.relation else "X"
        phone_number = nominee.phone_number if nominee.phone_number else "X"
        address = nominee.address if nominee.address else "X"

        rows.append([
            member,
            full_name,
            relation,
            phone_number,
            address,
        ])

    table = _make_report_table(
        ["Member", "Nominee Name", "Relation", "Phone Number", "Address"],
        rows,
        PAGE_SIZE[0] - PAGE_LEFT - PAGE_RIGHT,
        proportions=[1.8, 1.5, 1.0, 1.35, 2.0],
    )
    return _build_report(response, "Nominee List Reports", table)


# ---------------------------------------------------------------------------
# Export single transaction invoice PDF
# ---------------------------------------------------------------------------

def download_invoice_report(id):
    response = _create_pdf_response(f"invoice_report_id_{id}.pdf")

    invoice = PaymentModel.objects.get(id=id)

    payment_type = invoice.payment_type if invoice.payment_type else "X"
    payment_method = invoice.payment_method if invoice.payment_method else "X"
    amount_of_money = invoice.amount_of_money if invoice.amount_of_money else "X"
    status = invoice.status if invoice.status else "X"
    pay_date = f"{invoice.pay_year} / {invoice.pay_month}"

    rows = [[
        str(payment_type),
        str(payment_method),
        str(amount_of_money),
        str(pay_date),
        str(status),
    ]]

    table = _make_report_table(
        ["Payment Type", "Payment Method", "Amount", "Date", "Progress Status"],
        rows,
        PAGE_SIZE[0] - PAGE_LEFT - PAGE_RIGHT,
        proportions=[1.6, 1.6, 1.0, 1.0, 1.4],
    )
    return _build_report(
        response,
        "Invoice Reports",
        table,
        department="UNITY POWER FINANCE DEPARTMENT",
    )


# ---------------------------------------------------------------------------
# Export all transaction list PDF
# ---------------------------------------------------------------------------

def download_transaction_list_report(request):
    response = _create_pdf_response("finance_transactions_list_report.pdf")

    transaction_list = PaymentModel.objects.all().order_by("-id")
    rows = []

    for transaction in transaction_list:
        member = transaction.user.email if transaction.user.email else "X"
        payment_type = transaction.payment_type if transaction.payment_type else "X"
        payment_method = transaction.payment_method if transaction.payment_method else "X"
        amount_of_money = transaction.amount_of_money if transaction.amount_of_money else "X"
        cashier = transaction.cashier if transaction.cashier else "X"
        status = transaction.status if transaction.status else "X"
        pay_date = f"{transaction.pay_year} / {transaction.pay_month}"

        rows.append([
            str(member),
            str(payment_type),
            str(payment_method),
            str(amount_of_money),
            str(cashier),
            str(status),
            str(pay_date),
        ])

    table = _make_report_table(
        ["Member", "Payment Type", "Payment Method", "Amount", "Cashier", "Status", "Date"],
        rows,
        PAGE_SIZE[0] - PAGE_LEFT - PAGE_RIGHT,
        proportions=[2.0, 1.2, 1.35, 1.0, 1.1, 1.0, 1.0],
        compact=True,
    )
    return _build_report(
        response,
        "Transactions List Reports",
        table,
        department="UNITY POWER FINANCE DEPARTMENT",
    )


# ---------------------------------------------------------------------------
# Export unpaid members list PDF
# ---------------------------------------------------------------------------

def download_unpaid_list_report(request):
    response = _create_pdf_response("finance_due_members_list_report.pdf")

    users = User.objects.all().order_by("-id")
    reports_data = calculate_all_users_billing(users)
    transaction_list = PaymentModel.objects.all().order_by("-id")

    rows = []

    for user in reports_data:
        member = str(user["email"]) if user["email"] else "X"
        account_number = str(user["account_number"]) if user["account_number"] else "X"
        due_months = str(user["total_unpaid_months"]) if user["total_unpaid_months"] else "X"
        total_due_amount = str(user["total_unpaid"]) if user["total_unpaid"] else "X"

        rows.append([
            member,
            account_number,
            due_months,
            total_due_amount + " TK",
        ])

    table = _make_report_table(
        ["Member", "ID Number", "Total Due Month", "Total Due Amount"],
        rows,
        PAGE_SIZE[0] - PAGE_LEFT - PAGE_RIGHT,
        proportions=[2.2, 1.2, 1.25, 1.35],
    )
    return _build_report(
        response,
        "Due Members List Reports",
        table,
        department="UNITY POWER FINANCE DEPARTMENT",
    )
