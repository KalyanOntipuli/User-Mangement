from datetime import datetime
import pytz


def get_current_time():
    ist = pytz.timezone("Asia/Kolkata")
    current_time_utc = datetime.now(pytz.utc)
    current_time_ist = current_time_utc.astimezone(ist)

    return current_time_ist