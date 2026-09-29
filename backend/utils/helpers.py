from datetime import datetime


# ==========================================
# VALIDATE DATE
# ==========================================

def is_valid_date(date_string):

    try:

        datetime.strptime(
            date_string,
            "%Y-%m-%d"
        )

        return True

    except (
        ValueError,
        TypeError
    ):

        return False


# ==========================================
# CLEAN TEXT
# ==========================================

def clean_text(value):

    if value is None:

        return ""

    return str(value).strip()