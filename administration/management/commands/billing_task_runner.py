from django.core.management.base import BaseCommand
from administration.tasks import enqueue_billing_sync_if_idle

class Command(BaseCommand):
    help = "Enqueues a billing reconciliation task when one is not already active."

    def handle(self, *args, **options):
        if enqueue_billing_sync_if_idle():
            self.stdout.write(self.style.SUCCESS("Billing reconciliation enqueued."))
        else:
            self.stdout.write(self.style.WARNING("Billing reconciliation is already queued or running."))
