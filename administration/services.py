# myapp/services.py
from django.conf import settings
from twilio.rest import Client

def send_whatsapp_message(to_number, message_body):
    """
    Sends a WhatsApp message using the Twilio API.
    to_number: Expected format '+1234567890'
    """
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    
    # Format the numbers explicitly for WhatsApp
    from_whatsapp = settings.TWILIO_WHATSAPP_NUMBER
    to_whatsapp = f"whatsapp:{to_number}"
    
    try:
        message = client.messages.create(
            body=message_body,
            from_=from_whatsapp,
            to=to_whatsapp
        )
        return message.sid
    except Exception as e:
        print(f"Error sending WhatsApp message: {e}")
        return None
