from datetime import datetime, timedelta
import time




def send_whatsapp_messages():
    import requests
    from django.conf import settings
    from membership.models import User
    
    url = f"https://graph.facebook.com/{settings.WHATSAPP_API_VERSION}/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    users = User.objects.all().order_by('-id')
    text_body = f"*UnityPower Association* \n\nশুভ সকাল। প্রতিভার জোরে আমরা কাজ শুরু করতে পারি, কিন্তু দলগত একতা আর সমন্বয়ের মাধ্যমেই আমরা সাফল্যে পৌঁছাতে পারি। একতাই শক্তি, একতাই প্রগতি। আজকের দিনটি সবার জন্য সফল হোক! \n\n*Best Regards,* \n*Finance Department*"

    for user in users:
        if user.profile.phone_number:
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": user.profile.phone_number,
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
        else:
            continue




def run_every_morning():
    while True:
        now = datetime.now()
        
        # Define the target time for today
        target_time = now.replace(hour=20, minute=19, second=0, microsecond=0)
        
        # If the target time has already passed today, schedule it for tomorrow
        if now >= target_time:
            target_time += timedelta(days=1)
        
        # Calculate how many seconds to wait
        seconds_to_wait = (target_time - now).total_seconds()
        print(f"Waiting {seconds_to_wait:.0f} seconds until the next execution at {target_time.strftime('%H:%M')}...")
        
        # Sleep until the exact morning time
        time.sleep(seconds_to_wait)
        
        # Execute your function
        send_whatsapp_messages()

if __name__ == "__main__":
    # Schedule to run every morning at 08:30 AM
    run_every_morning()
