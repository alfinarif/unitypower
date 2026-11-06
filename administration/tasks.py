from django.tasks import task
from django_tasks_db.models import DBTaskResult

from administration.helpers.user_payment_tasks import (
    calculate_and_sync_payment_summaries,
    calculate_billing_summaries,
    generate_due_billings,
)


BILLING_TASK_PATH = "administration.tasks.billing_sync_bg_task"
ACTIVE_TASK_STATUSES = ("ENQUEUED", "RUNNING")


@task
def billing_sync_bg_task():
    run_billing_sync()


def run_billing_sync():
    generate_due_billings()
    calculate_billing_summaries()
    calculate_and_sync_payment_summaries()


def _enqueue_billing_sync():
    billing_sync_bg_task.enqueue()


def enqueue_billing_sync_if_idle():
    task_is_active = DBTaskResult.objects.filter(
        task_path=BILLING_TASK_PATH,
        status__in=ACTIVE_TASK_STATUSES,
    ).exists()
    if task_is_active:
        return False

    _enqueue_billing_sync()
    return True
