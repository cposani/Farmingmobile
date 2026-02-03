import os
import os
import resend

def send_email(to_email: str, subject: str, plain_text: str) -> int:
    """
    Minimal Resend email helper.
    Returns 200 on success.
    """
    api_key = os.getenv("RESEND_API_KEY")
    from_email = os.getenv("DEFAULT_FROM_EMAIL")

    if not api_key:
        raise RuntimeError("RESEND_API_KEY not set")
    if not from_email:
        raise RuntimeError("DEFAULT_FROM_EMAIL not set")

    resend.api_key = api_key

    params = {
        "from": from_email,
        "to": [to_email],
        "subject": subject,
        "text": plain_text,
    }

    response = resend.Emails.send(params)
    return 200
