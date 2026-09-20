# finance/middleware.py
from administration.helpers.user_payment_tasks import (
    generate_due_billings, 
    calculate_billing_summaries, 
    calculate_and_sync_payment_summaries
)

class AutoBillingSyncMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. This code executes on EVERY single page navigation/request
        try:
            print(f"[MIDDLEWARE] Path changed to {request.path}. Syncing balances...")
            generate_due_billings()
            calculate_billing_summaries()
            calculate_and_sync_payment_summaries()
            
        except Exception as e:
            print(f"[MIDDLEWARE ERROR] Sync failed: {e}")

        # 2. Let the user continue to their destination view safely
        response = self.get_response(request)
        return response
