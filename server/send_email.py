import os
import requests

MAILGUN_API_KEY = f"{os.environ.get('MAILGUN_API_KEY')}"

def send_email_notification(user, text):

	return requests.post(
		"https://api.mailgun.net/v3/sandbox813833e6e5ca4b3a92fd38b9e9cb14d8.mailgun.org/messages",
		auth=("api", MAILGUN_API_KEY),
		data={"from": "Mailgun Sandbox <postmaster@sandbox813833e6e5ca4b3a92fd38b9e9cb14d8.mailgun.org>",
			"to": "Shane Antonio <shane.antonio@gmail.com>",
			"subject": "Health Risk Notification",
			"text": text})
