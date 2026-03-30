from datetime import datetime
from app.utils.date_helpers import get_current_month_string, format_date_string


def test_get_current_month_string_format():
    result = get_current_month_string()
    # Should be in YYYY-MM format
    assert len(result) == 7
    assert result[4] == '-'
    year, month = result.split('-')
    assert year.isdigit()
    assert month.isdigit()


def test_format_date_string():
    dt = datetime(2024, 5, 15)
    assert format_date_string(dt) == "2024-05-15"


def test_format_date_string_none():
    assert format_date_string(None) is None
