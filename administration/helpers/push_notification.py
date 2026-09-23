# your_app/utils.py
import logging
from firebase_admin.messaging import Message, Notification
from firebase_admin.exceptions import FirebaseError
from fcm_django.models import FCMDevice

# Setup logging to catch potential Firebase errors in production
logger = logging.getLogger(__name__)

def send_notification_to_finance(user_id, title, body, click_action=None, data_payload=None):
    """
    Sends an FCM push notification to all active devices of a specific user.
    
    :param user_id: The primary key (ID) of the User model target.
    :param title: The bold header text of the notification banner.
    :param body: The descriptive text content under the title.
    :param click_action: Optional. Absolute or relative URL path to open when clicked.
    :param data_payload: Optional. Dictionary of custom key-value pairs for the frontend.
    """
    # 1. Look up all active devices assigned to this specific user
    devices = FCMDevice.objects.filter(user_id=user_id, active=True)
    
    if not devices.exists():
        logger.info(f"Notification skipped: User {user_id} has no active registered devices.")
        return False

    # 2. Build additional background properties if provided
    extra_data = data_payload if isinstance(data_payload, dict) else {}
    if click_action:
        extra_data['click_action'] = click_action

    try:
        # 3. Build and execute the Firebase dispatch message
        # Use message= keyword mapping to comply with modern fcm-django structural standards
        response = devices.send_message(
            message=Message(
                notification=Notification(
                    title=title,
                    body=body
                ),
                data=extra_data if extra_data else None
            )
        )
        logger.info(f"Notification sent successfully to User {user_id}: {response}")
        return True

    except FirebaseError as e:
        logger.error(f"Firebase server failed to deliver to User {user_id}: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error running notification pipeline for User {user_id}: {str(e)}")
        return False
