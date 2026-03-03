import re
from datetime import datetime

def validate_email(email):
    # Basic email regex
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def validate_amount(amount):
    try:
        val = float(amount)
        if val < 0:
            return False
        return True
    except (ValueError, TypeError):
        return False

def validate_date(date_string):
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False
