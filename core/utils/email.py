import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def send_email(to_email: str, subject: str, plain_text: str) -> int:
    """
    Minimal SendGrid API email helper.
    Returns SendGrid status code (202 on success).
    Raises RuntimeError if env vars missing.
    """
    api_key = os.getenv("SENDGRID_API_KEY")
    from_email = os.getenv("DEFAULT_FROM_EMAIL")

    if not api_key:
        raise RuntimeError("SENDGRID_API_KEY not set")
    if not from_email:
        raise RuntimeError("DEFAULT_FROM_EMAIL not set")

    message = Mail(
        from_email=from_email,
        to_emails=to_email,
        subject=subject,
        plain_text_content=plain_text,
    )

    sg = SendGridAPIClient(api_key)
    response = sg.send(message)
    return response.status_code
