import calendar
from datetime import date
from collections import defaultdict
from dateutil.relativedelta import relativedelta

from django.db.models import Q

from finance.models import FeeSchedule, PaymentRequestModel

# controll monthly and special fee from admin panel using FeeSchedule Models
def get_fee_for_month(month_number):
    """Returns 25000 for April (4) and November (11), otherwise 5000."""
    fee_schedule_obj = FeeSchedule.objects.last()
    base_fee = fee_schedule_obj.base_fee
    special_fee = fee_schedule_obj.special_fee

    if month_number in [4, 11]:
        return base_fee + special_fee  # Total 25000 or just 5000 total based on your business rule
    return base_fee

# return paid unpaid report per user
def calculate_per_user_billing(user):
    start_date = user.profile.created_date
    today = date.today()
    
    # Fetch all months the user has already paid for
    paid_months = set(
        user.payment_request.filter(Q(is_accept=True) & Q(status='Approved') & Q()).values_list('pay_year', 'pay_month', flat=False)
    )

    unpaid_months_list = []
    total_unpaid_amount = 0
    total_expected_amount = 0

    current_date = date(start_date.year, start_date.month, 1)
    end_date = date(today.year, today.month, 1)

    # Loop through every month from creation until the current month
    while current_date <= end_date:
        year = current_date.year
        month = current_date.month
        month_name = calendar.month_name[month]
        
        fee = get_fee_for_month(month)
        total_expected_amount += fee

        # Check if this specific month/year combination is unpaid
        if (year, month) not in paid_months:
            unpaid_months_list.append({
                'month_name': f"{month_name} {year}",
                'amount': fee
            })
            total_unpaid_amount += fee

        # Move to next month
        current_date += relativedelta(months=1)

    return {
        'unpaid_months': unpaid_months_list,
        'total_unpaid_due': total_unpaid_amount,
        'total_expected_amount': total_expected_amount
    }



# return paid unpaid report for all users
def calculate_all_users_billing(users):
    today = date.today()
    
    # 1. Bulk-fetch ALL payments to avoid hitting DB inside loops
    all_payments = PaymentRequestModel.objects.all()
    
    # Map user ID to a set of their paid (year, month) tuples
    paid_maps = defaultdict(set)
    for payment in all_payments:
        paid_maps[payment.user.id].add((payment.pay_year, payment.pay_month))

    all_users_report = []

    # 2. Process records in memory
    for user in users:
        start_date = user.profile.created_date
        user_id = user.id
        user_paid_months = paid_maps[user_id]

        unpaid_months_list = []
        total_unpaid_amount = 0

        current_date = date(start_date.year, start_date.month, 1)
        end_date = date(today.year, today.month, 1)

        while current_date <= end_date:
            year = current_date.year
            month = current_date.month
            
            if (year, month) not in user_paid_months:
                fee = get_fee_for_month(month)
                unpaid_months_list.append({
                    'month_name': f"{calendar.month_name[month]} {year}",
                    'amount': fee
                })
                total_unpaid_amount += fee

            current_date += relativedelta(months=1)

        all_users_report.append({
            'id': user.id,
            'email': user.email,
            'account_number': user.account_number,
            'created_at': user.profile.created_date,
            'unpaid_months': unpaid_months_list,
            'total_unpaid_months': len(unpaid_months_list),
            'total_unpaid': total_unpaid_amount,
        })

    return all_users_report












