from django.core.management.base import BaseCommand
from django_tasks_db.models import DBTaskResult # Import the queue engine table

from administration.tasks import due_billing_bg_tasks, calculate_billing_bg_tasks, payment_summery_bg_tasks

class Command(BaseCommand):
    help = "Kicks off the infinite background polling task loops safely without duplication."

    def handle(self, *args, **options):
        # 1. Fetch paths of your tasks to check against the queue database
        # This matches the names stored in your DBTaskResult admin panel
        task_names = {
            "due_billing": "administration.tasks.due_billing_bg_tasks",
            "calculate": "administration.tasks.calculate_billing_bg_tasks",
            "summary": "administration.tasks.payment_summery_bg_tasks",
        }

        # 2. Check if they are already enqueued or actively running
        active_tasks = DBTaskResult.objects.filter(
            status__in=['ENQUEUED', 'RUNNING']
        ).values_list('task_path', flat=True)

        # 3. Safely queue up due billing tasks
        if task_names["due_billing"] not in active_tasks:
            self.stdout.write("Enqueueing due billing task...")
            due_billing_bg_tasks.enqueue()
        else:
            self.stdout.write(self.style.WARNING("Due billing task is already running. Skipped."))

        # 4. Safely queue up calculate billing tasks
        if task_names["calculate"] not in active_tasks:
            self.stdout.write("Enqueueing calculation task...")
            calculate_billing_bg_tasks.enqueue()
        else:
            self.stdout.write(self.style.WARNING("Calculation task is already running. Skipped."))

        # 5. Safely queue up payment summary tasks
        if task_names["summary"] not in active_tasks:
            self.stdout.write("Enqueueing payment summary task...")
            payment_summery_bg_tasks.enqueue()
        else:
            self.stdout.write(self.style.WARNING("Payment summary task is already running. Skipped."))

        self.stdout.write(self.style.SUCCESS("Bg runner initial check complete!"))
