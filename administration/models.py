from django.db import models

from membership.models import User


# model to save whatsapp messages which is sended to user
class WhatsappNotificationModel(models.Model):
    users = models.ManyToManyField(User, related_name="whatsapp_notification")
    company = models.CharField(max_length=255, blank=True, null=True, default="UnityPower-একতাই শক্তি")
    message = models.TextField(blank=True, null=True)
    is_sended = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Notification for - {self.company}"
