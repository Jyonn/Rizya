import datetime

from QitianSDK import QitianManager
from SmartDjango import NetPacker

from Config.models import Config, CI

NetPacker.set_mode(debug=True)

QITIAN_APP_ID = Config.get_value_by_key(CI.QITIAN_APP_ID)
QITIAN_APP_SECRET = Config.get_value_by_key(CI.QITIAN_APP_SECRET)

SECRET_KEY = Config.get_value_by_key(CI.PROJECT_SECRET_KEY)
JWT_ENCODE_ALGO = Config.get_value_by_key(CI.JWT_ENCODE_ALGO)

qt_manager = QitianManager(QITIAN_APP_ID, QITIAN_APP_SECRET)


def time_dictor(v):
    if isinstance(v, datetime.datetime):
        return v.timestamp()
    return v


def int_or_float(number):
    try:
        number = int(number)
    except Exception:
        number = float(number)
    return number


def last_timer(last):
    if last == 0:
        return datetime.datetime.now()
    else:
        return datetime.datetime.fromtimestamp(last)
