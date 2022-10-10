import datetime
import re
from copy import copy
from time import perf_counter

from bson import ObjectId, errors
from django.utils import timezone
import jdatetime
from csv import DictWriter

from config.logger import logger
from config.settings import DEBUG


def datetime_now():
    return timezone.now()


def to_jalali(time):
    start_time = jdatetime.datetime.fromgregorian(datetime=time, locale='fa_IR')
    start_time = start_time.strftime("%Y-%m-%d %H:%M:%S")
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
        if DEBUG is False:
            return func(*args, **kwargs)
        start = perf_counter()
        response = func(*args, **kwargs)
        end = perf_counter()
        if hasattr(args[0], '__name__'):
            class_name = args[0].__name__
        else:
            class_name = args[0].__class__.__name__
        logger.info(f'Query --> {class_name}.{func.__name__}() --> {(end - start) * 1_000:.2} ms')

        return response

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


def traffic_output_validator(output):
    default_output = [{'isp_name': 'Other', 'date_hourly': [], 'accessed_bytes': []},
                      {'isp_name': 'MTN', 'date_hourly': [], 'accessed_bytes': []},
                      {'isp_name': 'MCI', 'date_hourly': [], 'accessed_bytes': []}]
    if 0 < len(output) < 3:
        for item in output:
            if item['isp_name'] == 'Other':
                default_output[0]['date_hourly'] = item['date_hourly']
                default_output[0]['accessed_bytes'] = item['accessed_bytes']
            if item['isp_name'] == 'MTN':
                default_output[1]['date_hourly'] = item['date_hourly']
                default_output[1]['accessed_bytes'] = item['accessed_bytes']
            if item['isp_name'] == 'MCI':
                default_output[2]['date_hourly'] = item['date_hourly']
                default_output[2]['accessed_bytes'] = item['accessed_bytes']
        output = default_output

    date_period = set((output[0]['date_hourly'] + output[1]['date_hourly'] + output[2]['date_hourly']))
    date_period = sorted(date_period, key=lambda x: datetime.datetime.strptime(x, '%Y-%m-%d-%H'))

    for i in range(0, 3):
        accessed_bytes = []
        for date in date_period:
            if date not in output[i]['date_hourly']:
                accessed_bytes.append(0)
            else:
                index = output[i]['date_hourly'].index(date)
                accessed_bytes.append(output[i]['accessed_bytes'][index])
        output[i]['accessed_bytes'] = accessed_bytes
        output[i]['date_hourly'] = date_period

    return output


def two_tuple_to_dic_convertor(dict_keys_tuple, dict_values_tuple_list):
    dic_list = []
    for value_list in dict_values_tuple_list:
        d = dict(zip(dict_keys_tuple, value_list))
        dic_list.append(d)
    return dic_list


def json_to_csv_convertor(dict_list, name, *args):
    with open(f'excels/{name}.csv', 'w') as outfile:
        writer = DictWriter(outfile, args)
        # TODO
        writer.writeheader()
        writer.writerows(dict_list)


def convert_datetime_to_date_hourly(date_time):
    return str(date_time.date()) + "-" + str(date_time.time().hour)
