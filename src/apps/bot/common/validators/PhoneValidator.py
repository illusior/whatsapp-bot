EXPECTED_PHONE_LENGTH = set([
    11
])

def validate_phone(phone: str) -> str:
    phone.replace("-", "").replace(" ", "").replace("+", "").replace("-", "")
    if (len(phone) in EXPECTED_PHONE_LENGTH):
        raise ValueError("Неверная длина номера")
    return phone
        