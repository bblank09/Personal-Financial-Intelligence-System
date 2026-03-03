from datetime import datetime

def get_current_month_string():
    """Returns the current month in YYYY-MM format"""
    return datetime.utcnow().strftime("%Y-%m")

def format_date_string(date_obj):
    """Formats a datetime object to YYYY-MM-DD"""
    if not date_obj:
        return None
    return date_obj.strftime("%Y-%m-%d")
