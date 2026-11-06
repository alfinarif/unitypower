from django.core.management.base import BaseCommand

from administration.helpers.auto_whatsapp import run_every_morning


class Command(BaseCommand):
    help = "Run the daily WhatsApp scheduler in a dedicated process."

    def handle(self, *args, **options):
        run_every_morning()
