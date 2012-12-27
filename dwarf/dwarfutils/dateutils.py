import datetime
import calendar

import pytz


def datetime_now_utc():
    """Returns the current datetime in utc format"""
    return datetime.datetime.utcnow().replace(tzinfo=pytz.utc)


def unix_now_utc():
    """Returns the current unixtimestamp in utc format"""
    return datetime_to_unix(datetime_now_utc())


def datetime_to_unix(date):
    """converts datetime format to unix timestamp"""
    return calendar.timegm(date.utctimetuple())


def unix_to_datetime(unix_date, zone=pytz.utc):
    """Converts a unix timestamp to datetime format

    :param unix_date: the unix timestamp date
    :param zone: byu default is converted based on UTC, if we want to convert
    to other zone then pass this argument with the timezone
    """
    return datetime.datetime.fromtimestamp(int(unix_date), zone)


def datetime_utc_to_zone(date, zone):
    """Converts an UTC date to another date with a zone change
    for example a GMT+1 change: 13:00UTC -> 14:00n GMT+1

    :param date: the UTC date
    :param zone: the timezone
    """
    return date.astimezone(zone)
