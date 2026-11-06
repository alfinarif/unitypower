# finance/middleware.py
from administration.tasks import enqueue_billing_sync_if_idle

from django.urls import resolve, Resolver404


class AutoBillingSyncMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            current_url = resolve(request.path_info)
        except Resolver404:
            current_url = None

        if current_url and current_url.view_name in {
                'finance:approve_or_reject_payment_request', 
                'finance:payment_request', 
                'membership:summary_view',
                'finance:transaction_list',
                'administration:admin_index',
                'administration:admin_transaction_list',
                'administration:admin_unpaid_report_list',
        }:
            enqueue_billing_sync_if_idle()

        return self.get_response(request)