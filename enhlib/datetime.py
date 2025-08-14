from .stdlib.datetime import date, time, datetime

try:
    from dbf import Date, Time, DateTime
    dates = date, Date
    times = time, Time
    datetimes = datetime, DateTime
except ImportError:
    dates = date,
    times = time,
    datetimes = datetime,

moments = dates + times + datetimes
