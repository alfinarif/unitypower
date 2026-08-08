from datetime import date
from dateutil.relativedelta import relativedelta
from django.db.models import Q


from membership.models import User
from finance.models import PaymentRequestModel


def get_unpaid_report(request):
    MONTHLY_FEE = 5000.00 # Define your fixed monthly fee
    today = date.today()
    unpaid_users_report = []

    users = User.objects.select_related('profile').all()
    for member in users:
        start_date = member.profile.created_date

            # 1. Generate all expected payment months from creation until today
        expected_months = []
        expected_month_numbers = []
        current_month = start_date.replace(day=1)
        while current_month <= today.replace(day=1):
            expected_months.append(current_month)
            current_month += relativedelta(months=1)
            expected_month_numbers.append(current_month.month)
            

        # 2. Get months the user actually paid for
        paid_months = set(
            PaymentRequestModel.objects.filter(Q(user=member) & Q(is_accept=True) & Q(status='Approved'))
            .values_list('pay_month', flat=True)
        )
        # 3. Filter out paid months to find unpaid ones
        unpaid_months = [m for m in expected_months if m not in paid_months]
        
        # 4. Calculate totals if they due money
        if unpaid_months:
            total_due = len(unpaid_months) * MONTHLY_FEE
            unpaid_users_report.append({
                'user': member,
                'unpaid_months': [m.strftime('%B %Y') for m in unpaid_months],
                'total_unpaid_months': len(unpaid_months),
                'total_amount_due': total_due
            })
    return unpaid_users_report



def get_unpaid_report_per_user(user_id):
    MONTHLY_FEE = 5000.00 # Define your fixed monthly fee
    today = date.today()
    unpaid_users_report = []

    member = User.objects.select_related('profile').get(id=user_id)
    start_date = member.profile.created_date

    # 1. Generate all expected payment months from creation until today
    expected_months = []
    expected_month_numbers = []
    current_month = start_date.replace(day=1)
    while current_month <= today.replace(day=1):
        expected_months.append(current_month)
        current_month += relativedelta(months=1)
        expected_month_numbers.append(current_month.month)
        

    # 2. Get months the user actually paid for
    paid_months = set(
        PaymentRequestModel.objects.filter(Q(user=member) & Q(is_accept=True) & Q(status='Approved'))
        .values_list('pay_month', flat=True)
    )
    # 3. Filter out paid months to find unpaid ones
    unpaid_months = [m for m in expected_months if m not in paid_months]
    
    # 4. Calculate totals if they due money
    if unpaid_months:
        total_due = len(unpaid_months) * MONTHLY_FEE
        unpaid_users_report.append({
            'user': member,
            'unpaid_months': [m.strftime('%B %Y') for m in unpaid_months],
            'total_unpaid_months': len(unpaid_months),
            'total_amount_due': total_due
        })
    return unpaid_users_report








