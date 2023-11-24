import os
import requests
from string import Template 

MAILGUN_API_KEY = f"{os.environ.get('MAILGUN_API_KEY')}"

template = Template("""Hi Joe,

The following user requires professional intervention:
    UserId: $userId
    Name: $name
    Phone: $phone
    Reason: $reason

Click here for for more details.

AIDE-AIML
""") 


def send_email_notification(user, reason):

	text = template.substitute({'userId': user["userId"],
	    'name': user["name"],
    	'phone': user["phone"],
    	'reason': reason})

	return requests.post(
		"https://api.mailgun.net/v3/sandbox813833e6e5ca4b3a92fd38b9e9cb14d8.mailgun.org/messages",
		auth=("api", MAILGUN_API_KEY),
		data={"from": "Mailgun Sandbox <postmaster@sandbox813833e6e5ca4b3a92fd38b9e9cb14d8.mailgun.org>",
#			"to": "Joe Gulay <joegulay@gmail.com>",
			"to": "Shane Antonio <shane.antonio@gmail.com>",
			"subject": "AIDE-AIML: Professional Intervention Required",
			"text": text})
