def validate_phone(phone: str) -> str:
    phone.replace("-", "").replace(" ", "").replace("+", "").replace(
        "-", ""
    ).replace("(", "").replace(")", "")

    return phone
