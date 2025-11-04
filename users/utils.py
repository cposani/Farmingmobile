from django.core import signing

def generate_temp_token(otp_id, ttl_minutes=10):
    return signing.dumps({"otp_id": otp_id}, salt="password-reset")

def verify_temp_token(token, ttl_minutes=10):
    try:
        data = signing.loads(token, salt="password-reset", max_age=ttl_minutes*60)
        return data.get("otp_id")
    except signing.BadSignature:
        return None
