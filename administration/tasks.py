import calendar
from datetime import date
from collections import defaultdict
from dateutil.relativedelta import relativedelta
import time  # 1. IMPORT THIS

from django.tasks import task
from django.utils import timezone
from datetime import timedelta
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.db.models import Sum
from decimal import Decimal

from membership.models import User
from finance.models import FeeSchedule, PaymentModel, DuePayment, PaymentSummery


def get_fee_for_month(month_number):
    """Returns 25000 for April (4) and November (11), otherwise 5000."""
    fee_schedule_obj = FeeSchedule.objects.last()
    
    if not fee_schedule_obj:
        base_fee = 5000
        special_fee = 20000
    else:
        base_fee = fee_schedule_obj.base_fee
        special_fee = fee_schedule_obj.special_fee

    penalty_fine = 500
    today = date.today()
    if today.day > 10 and today.day <= 15:
        if month_number in [4, 11]:
            return base_fee + special_fee + penalty_fine
        return base_fee + penalty_fine
    else:
        if month_number in [4, 11]:
            return base_fee + special_fee
        return base_fee


# 2. REMOVE the non-standard periodic_task decorator. Use ONLY native @task.
@task
def due_billing_bg_tasks():
    try:
        with transaction.atomic():
            users = User.objects.all()
            today = date.today()
            
            all_payments = PaymentModel.objects.all()
            paid_maps = defaultdict(set)
            for payment in all_payments:
                paid_maps[payment.user.id].add((payment.pay_year, payment.pay_month))


            for user in users:
                if not hasattr(user, 'profile') or not user.profile.created_date:
                    continue
                    
                start_date = user.profile.created_date
                user_id = user.id
                user_paid_months = paid_maps[user_id]

                current_date = date(start_date.year, start_date.month, 1)
                end_date = date(today.year, today.month, 1)

                while current_date <= end_date:
                    year = current_date.year
                    month = current_date.month
                    
                    if (year, month) not in user_paid_months:
                        fee = get_fee_for_month(month)

                        due_payment, created = DuePayment.objects.get_or_create(
                            user=user,
                            pay_year=year,
                            pay_month=month,
                            due_amount=fee,
                            status='Pending'
                        )
                        if created:
                            print(f"Generated dues for User {user.id} - {month}/{year}")

                        if today.day > 10:
                            due_payment.is_penalty = True
                            due_payment.penalty_fee = 500.00
                            due_payment.save()

                    current_date += relativedelta(months=1)
                    
    except Exception as e:
        print(f"[Due Billing ERROR] Due Billing logic failed: {e}")

    # Since this runs inside the separate 'db_worker' process, sleeping here safely 
    # waits 10 seconds without locking up your main web server or website users.
    time.sleep(10)
    
    print("[Due Billing] Successfully executed the task...")
    due_billing_bg_tasks.enqueue()  # No arguments = completely safe from JSON serialization errors!




@task
def calculate_billing_bg_tasks():
    try:
        # Wrap everything in a single database transaction block
        with transaction.atomic():
            
            # Step 1: Query database totals instantly
            payment_totals = PaymentModel.objects.filter(status='Approved').values(
                'user', 'pay_year', 'pay_month'
            ).annotate(
                total_paid=Sum('amount_of_money')
            )

            # Step 2: Clear/Process tracking
            for record in payment_totals:
                user_id = record['user']
                year = record['pay_year']
                month = record['pay_month']
                total_paid = Decimal(record['total_paid'] or 0)

                # Find the target month due record
                due_payments = DuePayment.objects.filter(
                    user=user_id,
                    pay_year=year,
                    pay_month=month
                )
                
                for due in due_payments:
                    # FIX: Get the original absolute fee required for that specific month
                    original_base_fee = Decimal(get_fee_for_month(month))
                    
                    # FIX: Always calculate the remaining balance from the fresh original fee 
                    # This prevents negative loops and keeps data 100% correct
                    new_due_balance = original_base_fee - total_paid
                    
                    # Prevent setting negative numbers if they overpaid
                    if new_due_balance < 0:
                        new_due_balance = Decimal(0)

                    # Update if the number has actually changed to save DB write operations
                    if due.due_amount != new_due_balance:
                        due.due_amount = new_due_balance
                        due.save()

    except Exception as e:
        print(f"[Calculate billing ERROR] Calculate billing logic failed: {e}")

    # 3. Continuous Safe Background Loop
    time.sleep(10)
    
    print("[Calculate Billing] Successfully executed the task...")
    calculate_billing_bg_tasks.enqueue()



@task
def payment_summery_bg_tasks():
    print("[Payment Summary] Started payment summary processing loop...")
    
    try:
        with transaction.atomic():
            # 1. Calculate ONLY Payment Totals (No Join Conflict)
            payment_data = PaymentModel.objects.filter(status='Approved').values('user_id').annotate(
                total_paid=Sum('amount_of_money')
            )
            # Map user_id -> total_paid
            paid_map = {item['user_id']: Decimal(item['total_paid'] or 0) for item in payment_data}

            # 2. Calculate ONLY Due & Penalty Totals (No Join Conflict)
            due_data = DuePayment.objects.values('user_id').annotate(
                total_due=Sum('due_amount'),
                total_penalty=Sum('penalty_fee', filter=Q(is_penalty=True))
            )
            # Map user_id -> (total_due, total_penalty)
            due_map = {
                item['user_id']: (Decimal(item['total_due'] or 0), Decimal(item['total_penalty'] or 0)) 
                for item in due_data
            }

            # 3. Process every user cleanly using our safe memory maps
            users = User.objects.all()
            for user in users:
                total_paid = paid_map.get(user.id, Decimal('0.00'))
                total_due, total_penalty = due_map.get(user.id, (Decimal('0.00'), Decimal('0.00')))

                # 4. Use select_for_update to avoid any concurrency issues
                summary_queryset = PaymentSummery.objects.select_for_update().filter(user=user)

                if summary_queryset.exists():
                    summary_queryset.update(
                        total_due_amount=total_due,
                        total_penalty_amount=total_penalty,
                        total_paid_amount=total_paid
                    )
                else:
                    try:
                        PaymentSummery.objects.create(
                            user=user,
                            total_due_amount=total_due,
                            total_penalty_amount=total_penalty,
                            total_paid_amount=total_paid,
                            is_active=True
                        )
                    except IntegrityError:
                        PaymentSummery.objects.filter(user=user).update(
                            total_due_amount=total_due,
                            total_penalty_amount=total_penalty,
                            total_paid_amount=total_paid
                        )

            print("[Payment Summary] Sync complete with exact, non-doubled values.")

    except Exception as e:
        print(f"[Payment Summary ERROR] Payment summary logic failed: {e}")

    # 5. Continuous Loop Rescheduling
    print("[Payment Summary] Waiting 10 seconds before scheduling next block...")
    time.sleep(10)
    
    print("[Payment Summary] Spawning next task...")
    payment_summery_bg_tasks.enqueue()














