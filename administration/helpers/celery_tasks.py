# myapp/tasks.py
from celery import shared_task

from membership.models import User
from finance.models import PaymentRequestModel

@shared_task
def create_monthly_fee_object_for_all_member():
    users = User.objects.exclude(user_type='Developer')
    
    for user in users:
        PaymentRequestModel.objects.create(
            user= user,
            calculation_type = "Savings",
            payment_method = "Cash",
            amount_of_money = "5000",
            cashier = "Foysal-Ahammed",
        )
