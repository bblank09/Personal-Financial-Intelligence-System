from app.utils.validators import validate_email, validate_amount, validate_date


def test_validate_email_valid():
    assert validate_email("user@example.com") is True
    assert validate_email("name.surname@domain.co.th") is True


def test_validate_email_invalid():
    assert validate_email("notanemail") is False
    assert validate_email("@nodomain.com") is False
    assert validate_email("") is False


def test_validate_amount_valid():
    assert validate_amount(100) is True
    assert validate_amount(0) is True
    assert validate_amount("50.5") is True


def test_validate_amount_negative():
    assert validate_amount(-10) is False
    assert validate_amount("abc") is False
    assert validate_amount(None) is False


def test_validate_date_valid():
    assert validate_date("2024-05-01") is True
    assert validate_date("2023-12-31") is True


def test_validate_date_invalid():
    assert validate_date("01-05-2024") is False
    assert validate_date("not-a-date") is False
    assert validate_date("2024-13-01") is False
