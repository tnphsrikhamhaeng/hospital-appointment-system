from datetime import date

from dateutil.relativedelta import relativedelta


def normalize_name(value: str) -> str:
    return value.strip()


def normalize_username(value: str) -> str:
    return value.strip().lower()


def validate_date_of_birth(value: date) -> date:
    today = date.today()
    hundred_years_ago = today - relativedelta(years=100)

    if value > today:
        raise ValueError("Date of birth cannot be in the future.")

    if value < hundred_years_ago:
        raise ValueError("Age cannot be greater than 100 years.")

    return value


def validate_password_strength(value: str) -> str:
    special_characters = "@$!%*?&"

    if not any(c in special_characters for c in value):
        raise ValueError("Password must contain at least one special character.")

    return value
