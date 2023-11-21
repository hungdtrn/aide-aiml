import functions_framework
import storage
import google.cloud.logging
import logging
import send_email

client = google.cloud.logging.Client()
client.setup_logging()

promt="""

Example response:

Conversation:
"""


@functions_framework.http
def notification(request):
    yesterdayUsers = storage.yesterdaysUsers()
    if len(yesterdayUsers) == 0:
        print("No users updated their chat history yesterday")
    else:
        for userId in yesterdayUsers:
            history = storage.readHistory(userId)
            logging.info(history)

        """
                response = openai.completion(prompt + history)
                if response.score > threshold:
                    user = storage.readUser(user)
                    send_email.send_email_notification(user, response.description)
                else
                    print {user["userId"]}} less than threshold {response}
        """

    logging.info("Completed Successfully!")

    return "Completed Successfully!"


if __name__ == "__main__":
    notification(None)
    print("Done")