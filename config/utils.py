import re

from bson import ObjectId, errors
from django.utils import timezone
import jdatetime
from csv import DictWriter


def datetime_now():
    return timezone.now()


def to_jalali(time):
    start_time = jdatetime.datetime.fromgregorian(datetime=time, locale='fa_IR')
    return str(start_time)


def to_object_id(_id: str) -> ObjectId:
    if isinstance(_id, ObjectId):
        return _id
    try:
        return ObjectId(_id)
    except errors.InvalidId:
        raise "errors.InvalidId"


def query_logger(func):
    def log(*args, **kwargs):
        return func(*args, **kwargs)

    return log


def password_regex_check(password):
    rx = re.compile(r'^(?=.*\d).{8,}$')
    if not rx.match(password):
        return False
    return True


def email_regex_check(email):
    rx = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    if not rx.match(email):
        return False
    return True


def json_to_csv_convertor(dict_list, name, *args):
    with open(f'{name}.csv', 'w') as outfile:
        writer = DictWriter(outfile, args)
        writer.writeheader()
        writer.writerows(dict_list)


def convert_datetime_to_date_hourly(date_time):
    return str(date_time.date()) + "-" + str(date_time.time().hour)


def scale_traffic_time(traffics, type):
    if type[0] == 'Daily':
        for isp in traffics:
            for i in range(0, len(isp['data'])):
                for j in range(i, i + type[1]):
                    isp['data'][i]['accessed_bytes'] += isp['data'][j]['accessed_bytes']
    print(traffics)
    # elif type[0] == 'Hourly':