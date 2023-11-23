import datetime

def get_today():
    return datetime.datetime.now().strftime("%Y-%m-%d")

def get_now():
    return datetime.datetime.now().isoformat()
