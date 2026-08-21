# Email backend package for sending email
from mailersend import MailerSendClient, EmailBuilder
# dotenv for calling environent variables - loading all variables 
from dotenv import load_dotenv

# Load all environment variables from .env file
load_dotenv()


def send_email_notification():
    ms = MailerSendClient()

    email = (EmailBuilder()
            .from_email("info@unitypower.online", "Unity Power")
            .to_many([{"email": "alfindev7@gmail.com", "name": "Alfin Arif"}])
            .subject("Contact Us Messages")
            .html("Your messages has been sended successfully")
            .text("Your messages has been sended successfully")
            .build())

    response = ms.emails.send(email)



