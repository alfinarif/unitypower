from datetime import date
from dateutil.relativedelta import relativedelta
from django.db.models import Q

from itertools import groupby


from membership.models import User
from finance.models import FeeSchedule, PaymentRequestModel


def get_unpaid_report(request):
    MONTHLY_FEE = 5000.00 # Define your fixed monthly fee
    today = date.today()
    unpaid_users_report = []

    monthly_fee_obj = FeeSchedule.objects.last() # get fee amount object
    users = User.objects.select_related('profile').all() # get all user object


    for member in users:
        start_date = member.profile.created_date

        # 1. Generate all expected payment months from creation until today
        expected_months = []
        expected_month_and_fee = [] # get expected months from 1 to 12 and month fee
        unpaid_month_and_fee = [] # get unpaid months from 1 to 12 and month fee

        current_month = start_date.replace(day=1)
        while current_month <= today.replace(day=1):
            expected_months.append(current_month)
            current_month += relativedelta(months=1)      

            # get expected month and month fee
            monthly_fee = monthly_fee_obj.get_current_fee(current_month.month)
            expected_month_and_fee.append({
                'month': current_month,
                'month_fee': monthly_fee
            })

        # 2. Get months the user actually paid for
        paid_months = set(
            PaymentRequestModel.objects.filter(Q(user=member) & Q(is_accept=True) & Q(status='Approved'))
            .values_list('pay_month', flat=True)
        )
        
        # 3. Filter out paid months to find unpaid ones
        unpaid_months = [m for m in expected_months if m not in paid_months]

        # unpaid month and month fee
        for due_month in unpaid_months:
            # get unpaid month and month fee
            monthly_fee = monthly_fee_obj.get_current_fee(due_month.month)
            
            unpaid_month_and_fee.append({
                'user': member,
                'month_list': due_month.month,
                'month_fee': monthly_fee,
            })

        print(unpaid_month_and_fee['month_list'])
        # 4. Calculate totals if they due money
        if unpaid_months:
            total_due = len(unpaid_months) * MONTHLY_FEE
            unpaid_users_report.append({
                'user': member,
                'unpaid_months': [m.strftime('%B %Y') for m in unpaid_months],
                'total_unpaid_months': len(unpaid_months),
                'total_amount_due': total_due,
                'unpaid_month_and_fee': unpaid_month_and_fee,
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
    else:
        return []

    return []








