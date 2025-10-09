import datetime

from lib.exceptions import LibJusBrException


def to_date_time(date_str: str):
    if date_str.count('-') == 2 and date_str.count(':') == 2:
        return datetime.datetime.strptime(date_str[0:19], '%Y-%m-%d %H:%M:%S')
    if date_str.count('/') == 2 and date_str.count(':') == 2:
        return datetime.datetime.strptime(date_str[0:19], '%d/%m/%Y %H:%M:%S')
    raise LibJusBrException(f'cannot get date time from string {date_str}')


def to_date(date_str: str):
    if date_str.count('-') == 2:
        return datetime.datetime.strptime(date_str[0:10], '%Y-%m-%d').date()
    if date_str.count('/') == 2:
        return datetime.datetime.strptime(date_str[0:10], '%d/%m/%Y').date()
    raise LibJusBrException(f'cannot get date time from string {date_str}')


def is_date_time(date_str: str):
    return (
            date_str.count('-') == 2 or date_str.count('/') == 2
    ) and date_str.count(':') == 2
