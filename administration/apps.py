from django.apps import AppConfig
import threading

from administration.helpers.auto_whatsapp import run_every_morning




class AdministrationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'administration'


    def ready(self):
        # Starts the loop on a background thread so it doesn't block views
        # 'daemon=True' ensures the thread closes when the server stops
        threading.Thread(target=run_every_morning, daemon=True).start()