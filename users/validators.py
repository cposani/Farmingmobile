import re

def is_valid_phone(phone: str) -> bool:
    # Accept "+91XXXXXXXXXX" or "XXXXXXXXXX"
    return bool(re.fullmatch(r"(\+91)?[0-9]{10}", phone or ""))
