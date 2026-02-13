# import os
# import os
# import resend

# def send_email(to_email: str, subject: str, plain_text: str) -> int:
#     """
#     Minimal Resend email helper.
#     Returns 200 on success.
#     """
#     api_key = os.getenv("RESEND_API_KEY")
#     from_email = os.getenv("DEFAULT_FROM_EMAIL")

#     if not api_key:
#         raise RuntimeError("RESEND_API_KEY not set")
#     if not from_email:
#         raise RuntimeError("DEFAULT_FROM_EMAIL not set")

#     resend.api_key = api_key

#     params = {
#         "from": from_email,
#         "to": [to_email],
#         "subject": subject,
#         "text": plain_text,
#     }

#     response = resend.Emails.send(params)
#     return 200

from django.conf import settings
from sib_api_v3_sdk import Configuration, ApiClient, TransactionalEmailsApi, SendSmtpEmail
from sib_api_v3_sdk.rest import ApiException

def send_email(to_email: str, subject: str, plain_text: str) -> int:
    config = Configuration()
    config.api_key['api-key'] = settings.BREVO_API_KEY

    api_client = ApiClient(config)
    api_instance = TransactionalEmailsApi(api_client)

    email = SendSmtpEmail(
        to=[{"email": to_email}],
        sender={
            "email": settings.BREVO_SENDER_EMAIL,
            "name": settings.BREVO_SENDER_NAME,
        },
        subject=subject,
        text_content=plain_text,
    )

    try:
        api_instance.send_transac_email(email)
        return 200
    except ApiException as e:
        print("Brevo error:", e)
        return 500
