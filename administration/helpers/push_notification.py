# notifications/utils.py
from firebase_admin.messaging import Message, Notification
from fcm_django.models import FCMDevice

def alert_user_on_event(user_id, title_text, body_text):
    """
    Finds all active devices for a user and triggers an FCM push notification.
    """
    print('=============================test notification===============================================')
    devices = FCMDevice.objects.filter(user_id=user_id, active=True)
    
    if devices.exists():
        devices.send_message(
            Message(
                notification=Notification(
                    title=title_text,
                    body=body_text
                )
            )
        )
