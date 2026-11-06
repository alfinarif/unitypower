from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import Mock, call, patch

from django.test import SimpleTestCase

from administration.helpers.user_payment_tasks import get_fee_for_month
from administration.tasks import enqueue_billing_sync_if_idle, run_billing_sync


class MonthlyFeeTests(SimpleTestCase):
    def test_fee_uses_supplied_schedule_without_reloading_it(self):
        schedule = SimpleNamespace(
            base_fee=Decimal('5000.00'),
            special_fee=Decimal('20000.00'),
        )

        self.assertEqual(get_fee_for_month(4, schedule), Decimal('25000.00'))
        self.assertEqual(get_fee_for_month(5, schedule), Decimal('5000.00'))
        self.assertEqual(get_fee_for_month(4, None), Decimal('25000.00'))


class BillingTaskTests(SimpleTestCase):
    @patch('administration.tasks.calculate_and_sync_payment_summaries')
    @patch('administration.tasks.calculate_billing_summaries')
    @patch('administration.tasks.generate_due_billings')
    def test_billing_sync_runs_in_dependency_order(
        self,
        generate_due_billings,
        calculate_billing_summaries,
        calculate_and_sync_payment_summaries,
    ):
        calls = Mock()
        calls.attach_mock(generate_due_billings, 'generate')
        calls.attach_mock(calculate_billing_summaries, 'calculate')
        calls.attach_mock(calculate_and_sync_payment_summaries, 'summarize')

        run_billing_sync()

        self.assertEqual(calls.mock_calls, [
            call.generate(),
            call.calculate(),
            call.summarize(),
        ])

    @patch('administration.tasks._enqueue_billing_sync')
    @patch('administration.tasks.DBTaskResult.objects.filter')
    def test_enqueue_starts_task_when_none_is_active(
        self,
        filter_tasks,
        enqueue_task,
    ):
        filter_tasks.return_value.exists.return_value = False

        self.assertTrue(enqueue_billing_sync_if_idle())
        enqueue_task.assert_called_once_with()

    @patch('administration.tasks._enqueue_billing_sync')
    @patch('administration.tasks.DBTaskResult.objects.filter')
    def test_enqueue_skips_task_when_one_is_active(
        self,
        filter_tasks,
        enqueue_task,
    ):
        filter_tasks.return_value.exists.return_value = True

        self.assertFalse(enqueue_billing_sync_if_idle())
        enqueue_task.assert_not_called()
