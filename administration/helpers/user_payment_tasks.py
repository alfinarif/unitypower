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
        base_fee = Decimal('5000.00')
        special_fee = Decimal('20000.00')
    else:
        base_fee = Decimal(fee_schedule_obj.base_fee)
        special_fee = Decimal(fee_schedule_obj.special_fee)

    if month_number in [4, 11]:
        return base_fee + special_fee
    return base_fee




def generate_due_billings():
    try:
        with transaction.atomic():
            # 1. Safely fetch the Pending Status object instance
            pending_status_obj = 'Pending'
            
            # Exclude developers at the database layer
            users = User.objects.filter(~Q(user_type='Developer'))
            today = date.today()
            
            # Prefetch payments to build a quick lookup map in memory
            all_payments = PaymentModel.objects.all().select_related('user')
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
                        # Fetch the original clean monthly base fee requirements
                        base_fee = Decimal(get_fee_for_month(month))

                        # --- FIX 1: CALCULATE THE CHRONOLOGICAL PENALTY DEADLINE ---
                        # Create a date object representing the 10th day of THIS SPECIFIC billing month
                        penalty_deadline = date(year, month, 10)
                        
                        is_late = False
                        penalty_amt = Decimal('0.00')
                        
                        # If today's calendar date has passed that month's specific 10th-day deadline,
                        # it is officially late, and a permanent penalty fine is applied.
                        if today > penalty_deadline:
                            is_late = True
                            penalty_amt = Decimal('500.00')

                        # ---  INCLUDE PENALTY IN INITIAL DUE_AMOUNT ---
                        final_calculated_due = base_fee + penalty_amt

                        due_payment, created = DuePayment.objects.get_or_create(
                            user=user,
                            pay_year=year,
                            pay_month=month,
                            defaults={
                                'due_amount': final_calculated_due,
                                'status': pending_status_obj, # FIX 3: Assign object, not string
                                'is_penalty': is_late,
                                'penalty_fee': penalty_amt
                            }
                        )
                        
                        if created:
                            print(f"Generated dues for User {user.id} - {month}/{year} (Penalty Applied: {is_late})")
                        else:
                            # If the record already existed but was unpaid, and it just passed the 10th deadline today,
                            # lock in the penalty updates permanently:
                            if is_late and not due_payment.is_penalty:
                                due_payment.is_penalty = True
                                due_payment.penalty_fee = penalty_amt
                                due_payment.due_amount += penalty_amt # Add fine to their active debt
                                due_payment.save()
                                print(f"Locked in lifetime penalty for User {user.id} on overdue month {month}/{year}")

                    current_date += relativedelta(months=1)
                    
        print("[Due Billing] Successfully completed generating due billings with accurate penalties.")
                    
    except Exception as e:
        print(f"[Due Billing ERROR] Due Billing logic failed: {e}")
        raise e




def calculate_billing_summaries():
    print("[Calculate Billing] Started chronological billing deduction waterfall...")
    try:
        with transaction.atomic():
            # Fetch actual status objects if they are ForeignKeys in your real database schema
            # If they are CharFields, you can replace these with raw strings like 'Approved' / 'Pending'
            approved_status_obj = 'Approved'
            pending_status_obj = 'Pending'
            
            # Step 1: Calculate the absolute GRAND TOTAL paid by each user over their lifetime
            user_payments = PaymentModel.objects.filter(status='Approved').values('user_id').annotate(
                grand_total_paid=Sum('amount_of_money')
            )
            
            # Map user_id -> their absolute "wallet pool" of available cash
            user_cash_pools = {item['user_id']: Decimal(item['grand_total_paid'] or 0) for item in user_payments}

            # Step 2: Fetch ALL DuePayments ordered CHRONOLOGICALLY (Strictly exclude Developer users)
            all_due_records = DuePayment.objects.filter(
                ~Q(user__user_type='Developer')
            ).select_related('user').order_by('user_id', 'pay_year', 'pay_month')

            # Step 3: Process the chronological ledger waterfall
            for due in all_due_records:
                user_id = due.user_id
                
                # Fetch how much total lifetime cash this user has left inside their pool
                available_cash = user_cash_pools.get(user_id, Decimal('0.00'))
                
                # Look up what this month was originally supposed to cost
                original_base_fee = Decimal(get_fee_for_month(due.pay_month))

                # --- FIX: READ PRE-CALCULATED LIFETIME PENALTY DIRECTLY FROM THE ROW ---
                row_penalty_fee = Decimal(due.penalty_fee or 0)
                
                # Total cost for this month is always the base month cost + its permanent fine
                total_month_cost = original_base_fee + row_penalty_fee

                if available_cash >= total_month_cost:
                    # CASE A: User has enough cash in their pool to clear this month completely
                    new_due_balance = Decimal('0.00')
                    
                    # Deduct total month cost from their lifetime pool remainder
                    user_cash_pools[user_id] -= total_month_cost
                    
                    # Mark the record as completely settled
                    due.status = approved_status_obj
                    # Note: We do NOT set due.is_penalty = False or penalty_fee = 0 here. 
                    # Keeping them unchanged locks the penalty history into the row permanently.
                
                elif available_cash > 0:
                    # CASE B: User has some money left, but not enough to cover the whole month cost
                    new_due_balance = total_month_cost - available_cash
                    
                    # Exhaust their cash pool completely. No money left to roll over.
                    user_cash_pools[user_id] = Decimal('0.00')
                    due.status = pending_status_obj
                
                else:
                    # CASE C: User has no cash left in their pool. The month remains fully due with fine.
                    new_due_balance = total_month_cost
                    due.status = pending_status_obj

                # Save only if the balance or status actually changed to protect DB performance
                if due.due_amount != new_due_balance or due.status != due.status:
                    due.due_amount = new_due_balance
                    due.save()
                    print(f"Updated Due row for User {user_id} ({due.pay_month}/{due.pay_year}): Due = {due.due_amount}")

            # --- STEP 4: STORE THE LEFT OVER SURPLUS IN PAYMENTSUMMERY ---
            print("[Calculate Billing] Updating PaymentSummery tables with remaining balances...")
            for user_id, remaining_surplus in user_cash_pools.items():
                
                # Additional fallback check to ensure no developer profiles receive a summary record
                from membership.models import User
                target_user = User.objects.filter(id=user_id).first()
                if target_user and target_user.user_type == 'Developer':
                    continue
                
                # update_or_create works perfectly here because of your OneToOneField mapping
                PaymentSummery.objects.update_or_create(
                    user_id=user_id,
                    defaults={
                        'credit_amount': remaining_surplus, 
                        'is_active': True
                    }
                )
                if remaining_surplus > 0:
                    print(f"[SURPLUS PERSISTED] User {user_id} leftover balance of {remaining_surplus} stored in PaymentSummery credit_amount.")

        print("[Calculate Billing] Successfully completed billing sync with synchronized lifetime penalties.")

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
            users = User.objects.filter(~Q(user_type='Developer'))
            
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















