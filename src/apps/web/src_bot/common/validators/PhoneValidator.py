def validate_phone(phone: str) -> str:
    phone.replace("-", "").replace(" ", "").replace("+", "").replace(
        "-", ""
    ).replace("(", "").replace(")", "")

    if not phone.isdigit():
        raise ValueError("Wrong phone format")

    return phone
