# whatsapp_service.py
import requests
from django.conf import settings

def send_whatsapp_messages(recipient_phone, text_body):
    
    url = f"https://graph.facebook.com/{settings.WHATSAPP_API_VERSION}/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient_phone,
        "type": "text",
        "text": {
            "preview_url": True,
            "body": text_body
        }
    }


    
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()
        
        if response.status_code == 200:
            return {"success": True, "data": response_data}
        else:
            return {"success": False, "error": response_data}
            
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": str(e)}
