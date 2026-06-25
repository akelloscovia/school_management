import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
import os


def send_email(to_email, subject, html_content):
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = os.getenv("BREVO_API_KEY")

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )

    sender = {"email": os.getenv("SENDER_EMAIL"), "name": os.getenv("SENDER_NAME")}
    to = [{"email": to_email}]

    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=to, sender=sender, subject=subject, html_content=html_content
    )

    try:
        response = api_instance.send_transac_email(send_smtp_email)
        print("Email sent. Message ID:", response.message_id)
        return True
    except ApiException as e:
        print("Error sending email:", e)
        return False
