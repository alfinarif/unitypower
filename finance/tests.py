from types import SimpleNamespace
from unittest.mock import patch

from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase

from finance.middleware import AutoBillingSyncMiddleware


class AutoBillingSyncMiddlewareTests(SimpleTestCase):
    @patch('finance.middleware.enqueue_billing_sync_if_idle')
    @patch('finance.middleware.resolve')
    def test_selected_page_enqueues_background_sync(
        self,
        resolve,
        enqueue_billing_sync,
    ):
        resolve.return_value = SimpleNamespace(view_name='membership:summary_view')
        response = HttpResponse('ok')
        middleware = AutoBillingSyncMiddleware(lambda request: response)

        result = middleware(RequestFactory().get('/summary/'))

        self.assertIs(result, response)
        enqueue_billing_sync.assert_called_once_with()
