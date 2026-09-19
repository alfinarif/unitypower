from datetime import date, datetime
from collections import defaultdict
from django.utils import timezone
from decimal import Decimal
from dateutil.relativedelta import relativedelta
from django.db import transaction
from django.db.models import Sum, Q
from django.db.utils import IntegrityError

from finance.models import FeeSchedule, PaymentModel, DuePayment, PaymentSummery
from membership.models import User


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
    if today.day > 10:
        if month_number in [4, 11]:
            return base_fee + special_fee + penalty_fine
        return base_fee + penalty_fine
    else:
        if month_number in [4, 11]:
            return base_fee + special_fee
        return base_fee



def generate_due_billings():
    print("[Due Billing] Started generating due billings processing...")
    try:
        with transaction.atomic():
            users = User.objects.all()
            today = date.today()
            
            # Prefetch payments to build a quick lookup map in memory
            all_payments = PaymentModel.objects.all().select_related('user')
            paid_maps = defaultdict(set)
            for payment in all_payments:
                paid_maps[payment.user.id].add((payment.pay_year, payment.pay_month))

            for user in users:
                # Safe attribute extraction
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
                        # Fetch original monthly fee requirements
                        fee = get_fee_for_month(month)

                        due_payment, created = DuePayment.objects.get_or_create(
                            user=user,
                            pay_year=year,
                            pay_month=month,
                            defaults={
                                'due_amount': Decimal(fee),
                                'status': 'Pending'
                            }
                        )
                        
                        if created:
                            print(f"Generated dues for User {user.id} - {month}/{year}")

                        # Check if past grace period (10th day of the month)
                        if today.day > 10:
                            due_payment.is_penalty = True
                            due_payment.penalty_fee = Decimal('500.00')  # Keep Decimals consistent
                            due_payment.save()

                    current_date += relativedelta(months=1)
                    
        print("[Due Billing] Successfully completed generating due billings.")
                    
    except Exception as e:
        print(f"[Due Billing ERROR] Due Billing logic failed: {e}")
        raise e  # Re-raise so your calling framework knows it crashed




def calculate_billing_summaries():
    print("[Calculate Billing] Started chronological billing deduction waterfall...")
    try:
        with transaction.atomic():
            # 1. Fetch required status objects safely to prevent foreign key errors
            approved_status_obj = 'Approved'
            pending_status_obj = 'Pending'
            
            # Step 1: Calculate the absolute GRAND TOTAL paid by each user over their lifetime
            user_payments = PaymentModel.objects.filter(status='Approved').values('user_id').annotate(
                grand_total_paid=Sum('amount_of_money')
            )
            
            # Map user_id -> their absolute "wallet pool" of available cash
            # Example: { 1: Decimal('50000.00'), 2: Decimal('15000.00') }
            user_cash_pools = {item['user_id']: Decimal(item['grand_total_paid'] or 0) for item in user_payments}

            # Step 2: Fetch ALL DuePayments ordered CHRONOLOGICALLY
            # This is critical so old months get paid off before newer months
            all_due_records = DuePayment.objects.all().order_by('user_id', 'pay_year', 'pay_month')

            # Step 3: Process the chronological ledger waterfall
            for due in all_due_records:
                user_id = due.user_id
                
                # Fetch how much total lifetime cash this user has left inside their pool
                available_cash = user_cash_pools.get(user_id, Decimal('0.00'))
                
                # Look up what this month was originally supposed to cost
                original_base_fee = Decimal(get_fee_for_month(due.pay_month))

                if available_cash >= original_base_fee:
                    # CASE A: User has enough cash in their pool to clear this month completely
                    new_due_balance = Decimal('0.00')
                    
                    # Deduct this month's cost from their lifetime pool. 
                    # The remainder stays in user_cash_pools and naturally rolls over to the next loop iteration!
                    user_cash_pools[user_id] -= original_base_fee
                    
                    # Mark the record as completely settled
                    due.status = approved_status_obj
                    due.is_penalty = False
                    due.penalty_fee = Decimal(0)
                
                elif available_cash > 0:
                    # CASE B: User has some money left, but not enough to cover the whole month
                    new_due_balance = original_base_fee - available_cash
                    
                    # Exhaust their cash pool completely. No money left to roll over.
                    user_cash_pools[user_id] = Decimal('0.00')
                    due.status = pending_status_obj
                
                else:
                    # CASE C: User has no cash left in their pool. The month remains fully due.
                    new_due_balance = original_base_fee
                    due.status = pending_status_obj

                # Step 4: Save only if the balance or status actually changed to protect DB performance
                if due.due_amount != new_due_balance or due.status != due.status:
                    due.due_amount = new_due_balance
                    due.save()
                    print(f"Updated User {user_id} ({due.pay_month}/{due.pay_year}): Due Balance = {due.due_amount}, Status = {due.status}")

        print("[Calculate Billing] Successfully completed billing sync with rollover cascading.")

    except Exception as e:
        print(f"[Calculate billing ERROR] Calculate billing logic failed: {e}")
        raise e




def calculate_and_sync_payment_summaries():
    print("[Payment Summary] Started payment summary processing...")
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
                total_penalty=Sum('penalty_fee', filter=Q(is_penalty=True)),
            )
            
            # Map user_id -> (total_due, total_penalty)
            due_map = {
                item['user_id']: (Decimal(item['total_due'] or 0), Decimal(item['total_penalty'] or 0)) 
                for item in due_data
            }
            
            # 3. Process every user cleanly using safe memory maps
            # Note: For production with large databases, consider .iterator()
            users = User.objects.all()
            
            for user in users:
                total_paid = paid_map.get(user.id, Decimal('0.00'))
                total_due, total_penalty = due_map.get(user.id, (Decimal('0.00'), Decimal('0.00')))   

                # 4. Use select_for_update to avoid concurrency race-conditions
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
                        # Fallback if another thread created it at the exact same millisecond
                        PaymentSummery.objects.filter(user=user).update(
                            total_due_amount=total_due,
                            total_penalty_amount=total_penalty,
                            total_paid_amount=total_paid
                        )
                        
            print("[Payment Summary] Sync complete with exact, non-doubled values.")
            
    except Exception as e:
        print(f"[Payment Summary ERROR] Payment summary logic failed: {e}")
        raise e # Re-raise so your view or background runner knows it failed















