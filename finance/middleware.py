# finance/middleware.py
from administration.helpers.user_payment_tasks import (
    generate_due_billings, 
    calculate_billing_summaries, 
    calculate_and_sync_payment_summaries
)

from django.urls import resolve, Resolver404

class AutoBillingSyncMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response


    def __call__(self, request):
        try:
            # Resolve the current path back to its internal view details
            current_url = resolve(request.path_info)
            
            # Match against your specific URL pattern namespace or view names
            target_view_names = [
                'finance:approve_or_reject_payment_request', 
                'finance:payment_request', 
                'membership:summary_view',
                'finance:transaction_list',
                'administration:admin_index',
                'administration:admin_transaction_list',
                'administration:admin_unpaid_report_list',
                ]
            
            if current_url.view_name in target_view_names:
                print(f"[MIDDLEWARE] Path hit! to {request.path}. For Syncing balances...")
                generate_due_billings()
                calculate_billing_summaries()
                calculate_and_sync_payment_summaries()
                
        except Resolver404:
            # Fallback if the requested URL doesn't match any route in your application
            pass
        except Exception as e:
            print(f"[MIDDLEWARE ERROR] Logic failure: {e}")

        response = self.get_response(request)
        return response