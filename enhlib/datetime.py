from __future__ import print_function

from . import *
from .stdlib import datetime as dt
import sys
import time

if PY_VER < (3, 4):
    from aenum import Enum as _Enum, IntEnum as _IntEnum
else:
    from enum import Enum as _Enum, IntEnum as _IntEnum

try:
    import pytz
except ImportError:
    pytz = None

OD = 86400
OH = 3600
OM = 60
MILLION = 1000000

def _export(enum):
    globals().update(enum.__members__)
    return enum

    # dec jan feb mar apr may jun jul aug sep oct nov dec jan
days_per_month = [31, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31, 31]
days_per_leap_month = [31, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31, 31]

def days_in_month(year):
    return (days_per_month, days_per_leap_month)[is_leapyear(year)]

def is_leapyear(year):
    if year % 400 == 0:
        return True
    elif year % 100 == 0:
        return False
    elif year % 4 == 0:
        return True
    else:
        return False


## Constants

class IsoDay(_IntEnum):
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7

    def next_delta(self, day):
        """Return number of days needed to get from self to day."""
        if self == day:
            return 7
        delta = day - self
        if delta < 0:
            delta += 7
        return delta

    def last_delta(self, day):
        """Return number of days needed to get from self to day."""
        if self == day:
            return -7
        delta = day - self
        if delta > 0:
            delta -= 7
        return delta


@_export
class RelativeDay(_Enum):
    LAST_SUNDAY = ()
    LAST_SATURDAY = ()
    LAST_FRIDAY = ()
    LAST_THURSDAY = ()
    LAST_WEDNESDAY = ()
    LAST_TUESDAY = ()
    LAST_MONDAY = ()
    NEXT_MONDAY = ()
    NEXT_TUESDAY = ()
    NEXT_WEDNESDAY = ()
    NEXT_THURSDAY = ()
    NEXT_FRIDAY = ()
    NEXT_SATURDAY = ()
    NEXT_SUNDAY = ()

    def __new__(cls):
        result = object.__new__(cls)
        result._value = len(cls.__members__) + 1
        return result

    def days_from(self, day):
        target = IsoDay[self.name[5:]]
        if self.name[:4] == 'LAST':
            return day.last_delta(target)
        return day.next_delta(target)


class IsoMonth(_IntEnum):
    JANUARY = 1
    FEBRUARY = 2
    MARCH = 3
    APRIL = 4
    MAY = 5
    JUNE = 6
    JULY = 7
    AUGUST = 8
    SEPTEMBER = 9
    OCTOBER = 10
    NOVEMBER = 11
    DECEMBER = 12

    def next_delta(self, month):
        """Return number of months needed to get from self to month."""
        if self == month:
            return 12
        delta = month - self
        if delta < 0:
            delta += 12
        return delta

    def last_delta(self, month):
        """Return number of months needed to get from self to month."""
        if self == month:
            return -12
        delta = month - self
        if delta > 0:
            delta -= 12
        return delta


@_export
class RelativeMonth(_Enum):
    LAST_DECEMBER = ()
    LAST_NOVEMBER = ()
    LAST_OCTOBER = ()
    LAST_SEPTEMBER = ()
    LAST_AUGUST = ()
    LAST_JULY = ()
    LAST_JUNE = ()
    LAST_MAY = ()
    LAST_APRIL = ()
    LAST_MARCH= ()
    LAST_FEBRUARY = ()
    LAST_JANUARY = ()
    NEXT_JANUARY = ()
    NEXT_FEBRUARY = ()
    NEXT_MARCH = ()
    NEXT_APRIL = ()
    NEXT_MAY = ()
    NEXT_JUNE = ()
    NEXT_JULY = ()
    NEXT_AUGUST = ()
    NEXT_SEPTEMBER = ()
    NEXT_OCTOBER = ()
    NEXT_NOVEMBER = ()
    NEXT_DECEMBER = ()

    def __new__(cls):
        result = object.__new__(cls)
        result._value = len(cls.__members__) + 1
        return result

    def months_from(self, month):
        target = IsoMonth[self.name[5:]]
        if self.name[:4] == 'LAST':
            return month.last_delta(target)
        return month.next_delta(target)


## wrappers around datetime and logical objects to allow null values

class Date(object):
    """
    adds null capable datetime.date constructs
    """

    __slots__ = ['_date']

    def __new__(cls, year=None, month=0, day=0):
        """
        date should be either a datetime.date or date/month/day should
        all be appropriate integers
        """
        if year is None:
            return cls._null_date
        nd = object.__new__(cls)
        if isinstance(year, basestring):
            return Date.strptime(year)
        elif isinstance(year, dt.date):
            nd._date = year
        elif isinstance(year, Date):
            nd._date = year._date
        else:
            nd._date = dt.date(year, month, day)
        return nd

    def __add__(self, other):
        if self and isinstance(other, timedeltas):
            return Date(self._date + other)
        else:
            return NotImplemented

    def __eq__(self, other):
        if isinstance(other, Date):
            return self._date == other._date
        if isinstance(other, dt.date):
            return self._date == other
        if other is None:
            return self._date is None
        return NotImplemented

    def __format__(self, spec):
        if self:
            return self._date.__format__(spec)
        return ''

    def __getattr__(self, name):
        if name == '_date':
            raise AttributeError('_date missing!')
        elif self:
            return getattr(self._date, name)
        else:
            raise AttributeError('NullDate object has no attribute %s' % name)

    def __ge__(self, other):
        if self:
            if isinstance(other, dt.date):
                return self._date >= other
            elif isinstance(other, Date):
                if other:
                    return self._date >= other._date
                return True
        else:
            if isinstance(other, dt.date):
                return False
            elif isinstance(other, Date):
                if other:
                    return False
                return True
        return NotImplemented

    def __gt__(self, other):
        if self:
            if isinstance(other, dt.date):
                return self._date > other
            elif isinstance(other, Date):
                if other:
                    return self._date > other._date
                return True
        else:
            if isinstance(other, dt.date):
                return False
            elif isinstance(other, Date):
                if other:
                    return False
                return False
        return NotImplemented

    def __hash__(self):
        return hash(self._date)

    def __le__(self, other):
        if self:
            if isinstance(other, dt.date):
                return self._date <= other
            elif isinstance(other, Date):
                if other:
                    return self._date <= other._date
                return False
        else:
            if isinstance(other, dt.date):
                return True
            elif isinstance(other, Date):
                if other:
                    return True
                return True
        return NotImplemented

    def __lt__(self, other):
        if self:
            if isinstance(other, dt.date):
                return self._date < other
            elif isinstance(other, Date):
                if other:
                    return self._date < other._date
                return False
        else:
            if isinstance(other, dt.date):
                return True
            elif isinstance(other, Date):
                if other:
                    return True
                return False
        return NotImplemented

    def __ne__(self, other):
        if self:
            if isinstance(other, dt.date):
                return self._date != other
            elif isinstance(other, Date):
                if other:
                    return self._date != other._date
                return True
        else:
            if isinstance(other, dt.date):
                return True
            elif isinstance(other, Date):
                if other:
                    return True
                return False
        return NotImplemented

    if PY_VER < (3, 0):
        def __nonzero__(self):
            return self._date is not None
    else:
        def __bool__(self):
            return self._date is not None

    __radd__ = __add__

    def __rsub__(self, other):
        if self and isinstance(other, dt.date):
            return TimeDelta(other - self._date)
        else:
            return NotImplemented

    def __repr__(self):
        if self:
            return "Date(%d, %d, %d)" % self.timetuple()[:3]
        else:
            return "Date()"

    def __str__(self):
        if self:
            return unicode(self._date)
        return ""

    def __sub__(self, other):
        if self and isinstance(other, dt.date):
            return TimeDelta(self._date - other)
        elif self and isinstance(other, Date):
            return TimeDelta(self._date - other._date)
        elif self and isinstance(other, timedeltas):
            return Date(self._date - other)
        else:
            return NotImplemented

    def date(self):
        if self:
            return self._date
        return None

    @classmethod
    def fromordinal(cls, number):
        if number:
            return cls(dt.date.fromordinal(number))
        return cls()

    @classmethod
    def fromtimestamp(cls, timestamp):
        return cls(dt.date.fromtimestamp(timestamp))

    @classmethod
    def fromymd(cls, yyyymmdd):
        if yyyymmdd in ('', '        ', 'no date', '00000000'):
            return cls()
        return cls(dt.date(int(yyyymmdd[:4]), int(yyyymmdd[4:6]), int(yyyymmdd[6:])))

    def replace(self, year=None, month=None, day=None, delta_year=0, delta_month=0, delta_day=0):
        if not self:
            return Date._null_date
        old_year, old_month, old_day = self.timetuple()[:3]
        if isinstance(month, RelativeMonth):
            this_month = IsoMonth(old_month)
            delta_month += month.months_from(this_month)
            month = None
        if isinstance(day, RelativeDay):
            this_day = IsoDay(self.isoweekday())
            delta_day += day.days_from(this_day)
            day = None
        year = (old_year if year is None else year) + delta_year
        month = (old_month if month is None else month) + delta_month
        day = (old_day if day is None else day) + delta_day
        days_in_month = (days_per_month, days_per_leap_month)[is_leapyear(year)]
        while not(0 < month < 13) or not (0 < day <= days_in_month[month]):
            while month < 1:
                year -= 1
                month += 12
            while month > 12:
                year += 1
                month -= 12
            days_in_month = (days_per_month, days_per_leap_month)[is_leapyear(year)]
            while day < 1:
                month -= 1
                day = days_in_month[month] + day
                if not 0 < month < 13:
                    break
            while day > days_in_month[month]:
                day -= days_in_month[month]
                month += 1
                if not 0 < month < 13:
                    break
        return Date(year, month, day)

    def strftime(self, format):
        fmt_cls = type(format)
        if self:
            return fmt_cls(self._date.strftime(format))
        return fmt_cls('')

    @classmethod
    def strptime(cls, date_string, format=None):
        if format is not None:
            return cls(*(time.strptime(date_string, format)[0:3]))
        return cls(*(time.strptime(date_string, "%Y-%m-%d")[0:3]))

    def timetuple(self):
        return self._date.timetuple()

    @classmethod
    def today(cls):
        return cls(dt.date.today())

    def ymd(self):
        if self:
            return "%04d%02d%02d" % self.timetuple()[:3]
        else:
            return '        '

Date.max = Date(dt.date.max)
Date.min = Date(dt.date.min)
Date._null_date = object.__new__(Date)
Date._null_date._date = None
NullDate = Date()


class DateTime(object):
    """
    adds null capable datetime.datetime constructs
    """

    __slots__ = ['_datetime']

    def __new__(cls, year=None, month=0, day=0, hour=0, minute=0, second=0, microsecond=0, tzinfo=None):
        """year may be a datetime.datetime"""
        if year is None:
            return cls._null_datetime
        ndt = object.__new__(cls)
        if isinstance(year, basestring):
            return DateTime.strptime(year)
        elif isinstance(year, DateTime):
            if tzinfo is not None and year._datetime.tzinfo:
                raise ValueError('not naive datetime (tzinfo is already set)')
            ndt._datetime = year._datetime
        elif isinstance(year, dt.datetime):
            if tzinfo is not None and year.tzinfo:
                raise ValueError('not naive datetime (tzinfo is already set)')
            elif tzinfo is None:
                tzinfo = year.tzinfo
            microsecond = int(year.microsecond)
            hour, minute, second = year.hour, year.minute, year.second
            year, month, day = year.year, year.month, year.day
            if pytz is None or tzinfo is None:
                ndt._datetime = dt.datetime(year, month, day, hour, minute, second, microsecond, tzinfo)
            else:
                # if pytz and tzinfo, tzinfo must be added after creation
                _datetime = dt.datetime(year, month, day, hour, minute, second, microsecond)
                ndt._datetime = tzinfo.normalize(tzinfo.localize(_datetime))
        elif year is not None:
            microsecond = int(microsecond)
            if pytz is None or tzinfo is None:
                ndt._datetime = dt.datetime(year, month, day, hour, minute, second, microsecond, tzinfo)
            else:
                # if pytz and tzinfo, tzinfo must be added after creation
                _datetime = dt.datetime(year, month, day, hour, minute, second, microsecond)
                ndt._datetime = tzinfo.normalize(tzinfo.localize(_datetime))
        return ndt

    def __add__(self, other):
        if self and isinstance(other, timedeltas):
            return DateTime(self._datetime + other)
        else:
            return NotImplemented

    def __eq__(self, other):
        if isinstance(other, DateTime):
            return self._datetime == other._datetime
        if isinstance(other, dt.date):
            me = self._datetime.timetuple()
            them = other.timetuple()
            return me[:6] == them[:6] and self.microsecond == int(other.microsecond)
        if other is None:
            return self._datetime is None
        return NotImplemented

    def __format__(self, spec):
        if self:
            return self._datetime.__format__(spec)
        return ''

    def __getattr__(self, name):
        if name == '_datetime':
            raise AttributeError('_datetime missing!')
        elif self:
            return getattr(self._datetime, name)
        else:
            raise AttributeError('NullDateTime object has no attribute %s' % name)

    def __ge__(self, other):
        if self:
            if isinstance(other, dt.datetime):
                return self._datetime >= other
            elif isinstance(other, DateTime):
                if other:
                    return self._datetime >= other._datetime
                return False
        else:
            if isinstance(other, dt.datetime):
                return False
            elif isinstance(other, DateTime):
                if other:
                    return False
                return True
        return NotImplemented

    def __gt__(self, other):
        if self:
            if isinstance(other, dt.datetime):
                return self._datetime > other
            elif isinstance(other, DateTime):
                if other:
                    return self._datetime > other._datetime
                return True
        else:
            if isinstance(other, dt.datetime):
                return False
            elif isinstance(other, DateTime):
                if other:
                    return False
                return False
        return NotImplemented

    def __hash__(self):
        return self._datetime.__hash__()

    def __le__(self, other):
        if self:
            if isinstance(other, dt.datetime):
                return self._datetime <= other
            elif isinstance(other, DateTime):
                if other:
                    return self._datetime <= other._datetime
                return False
        else:
            if isinstance(other, dt.datetime):
                return True
            elif isinstance(other, DateTime):
                if other:
                    return True
                return True
        return NotImplemented

    def __lt__(self, other):
        if self:
            if isinstance(other, dt.datetime):
                return self._datetime < other
            elif isinstance(other, DateTime):
                if other:
                    return self._datetime < other._datetime
                return False
        else:
            if isinstance(other, dt.datetime):
                return True
            elif isinstance(other, DateTime):
                if other:
                    return True
                return False
        return NotImplemented

    def __ne__(self, other):
        if self:
            if isinstance(other, dt.datetime):
                return self._datetime != other
            elif isinstance(other, DateTime):
                if other:
                    return self._datetime != other._datetime
                return True
        else:
            if isinstance(other, dt.datetime):
                return True
            elif isinstance(other, DateTime):
                if other:
                    return True
                return False
        return NotImplemented

    if PY_VER < (3, 0):
        def __nonzero__(self):
            return self._datetime is not None
    else:
        def __bool__(self):
            return self._datetime is not None

    __radd__ = __add__

    def __rsub__(self, other):
        if self and isinstance(other, dt.datetime):
            return TimeDelta(other - self._datetime)
        else:
            return NotImplemented

    def __repr__(self):
        if self:
            if self.tzinfo is None:
                tz = ''
            else:
                diff = self._datetime.utcoffset()
                hours, minutes = divmod(diff.days * OD + diff.seconds, OH)
                minus, hours = hours < 0, abs(hours)
                tz = ', tzinfo=<%s %s%02d%02d>' % (self._datetime.tzname(), ('','-')[minus], hours, minutes)
            return "DateTime(%d, %d, %d, %d, %d, %d, %d%s)" % (
                self._datetime.timetuple()[:6] + (self._datetime.microsecond, tz)
                )
        else:
            return "DateTime()"

    def __str__(self):
        if self:
            return unicode(self._datetime)
        return ""

    def __sub__(self, other):
        if self and isinstance(other, dt.datetime):
            return TimeDelta(self._datetime - other)
        elif self and isinstance(other, DateTime):
            return TimeDelta(self._datetime - other._datetime)
        elif self and isinstance(other, timedeltas):
            return DateTime(self._datetime - other)
        else:
            return NotImplemented

    @classmethod
    def combine(cls, date, time, tzinfo=None):
        # if tzinfo is given, timezone is added/stripped
        if tzinfo is None:
            tzinfo = time.tzinfo
        if Date(date) and Time(time):
            return cls(
                    date.year, date.month, date.day,
                    time.hour, time.minute, time.second, time.microsecond,
                    tzinfo=tzinfo,
                    )
        return cls()

    def date(self):
        if self:
            return Date(self.year, self.month, self.day)
        return Date()

    def datetime(self):
        if self:
            return self._datetime
        return None

    @classmethod
    def fromordinal(cls, number):
        if number:
            return cls(dt.datetime.fromordinal(number))
        else:
            return cls()

    @classmethod
    def fromtimestamp(cls, timestamp):
        return DateTime(dt.datetime.fromtimestamp(timestamp))

    @classmethod
    def now(cls, tzinfo=None):
        "only accurate to milliseconds"
        return cls(dt.datetime.now(), tzinfo=tzinfo)

    def replace(
            self,
            year=None, month=None, day=None, hour=None, minute=None, second=None, microsecond=None, tzinfo=None,
            delta_year=0, delta_month=0, delta_day=0, delta_hour=0, delta_minute=0, delta_second=0, delta_microsecond=0,
        ):
        if not self:
            return DateTime._null_datetime
        old_year, old_month, old_day, old_hour, old_minute, old_second = self.timetuple()[:6]
        old_micro = self.microsecond
        if tzinfo is None:
            tzinfo = self._datetime.tzinfo
        if isinstance(month, RelativeMonth):
            this_month = IsoMonth(old_month)
            delta_month += month.months_from(this_month)
            month = None
        if isinstance(day, RelativeDay):
            this_day = IsoDay(self.isoweekday())
            delta_day += day.days_from(this_day)
            day = None
        year = (old_year if year is None else year) + delta_year
        month = (old_month if month is None else month) + delta_month
        day = (old_day if day is None else day) + delta_day
        hour = (old_hour if hour is None else hour) + delta_hour
        minute = (old_minute if minute is None else minute) + delta_minute
        second = (old_second if second is None else second) + delta_second
        microsecond = (old_micro if microsecond is None else microsecond) + delta_microsecond
        days_in_month = (days_per_month, days_per_leap_month)[is_leapyear(year)]
        while (
                not (0 < month < 13)
             or not (0 < day <= days_in_month[month])
             or not (0 <= hour < 24)
             or not (0 <= minute < OM)
             or not (0 <= second < OM)
             or not (0 <= microsecond < MILLION)
            ):
            while month < 1:
                year -= 1
                month += 12
            while month > 12:
                year += 1
                month -= 12
            days_in_month = (days_per_month, days_per_leap_month)[is_leapyear(year)]
            while day < 1:
                month -= 1
                day += days_in_month[month]
                if not 0 < month < 13:
                    break
            while day > days_in_month[month]:
                day -= days_in_month[month]
                month += 1
                if not 0 < month < 13:
                    break
            while hour < 1:
                day -= 1
                hour += 24
            while hour > 23:
                day += 1
                hour -= 24
            while minute < 0:
                hour -= 1
                minute += OM
            while minute > 59:
                hour += 1
                minute -= OM
            while second < 0:
                minute -= 1
                second += OM
            while second > 59:
                minute += 1
                second -= OM
        return DateTime(year, month, day, hour, minute, second, microsecond, tzinfo)

    def strftime(self, format):
        fmt_cls = type(format)
        if self:
            return fmt_cls(self._datetime.strftime(format))
        return fmt_cls('')

    @classmethod
    def strptime(cls, datetime_string, format=None):
        if format is not None:
            return cls(dt.datetime.strptime(datetime_string, format))
        for format in (
                "%Y-%m-%d %H:%M:%S.%f",
                "%Y-%m-%d %H:%M:%S",
                ):
            try:
                return cls(dt.datetime.strptime(datetime_string, format))
            except ValueError:
                pass
        raise ValueError("Unable to convert %r" % datetime_string)

    def time(self):
        if self:
            return Time(self.hour, self.minute, self.second, self.microsecond)
        return Time()

    def timetuple(self):
        return self._datetime.timetuple()

    def timetz(self):
        if self:
            return Time(self._datetime.timetz())
        return Time()

    @classmethod
    def utcnow(cls):
        return cls(dt.datetime.utcnow())

    @classmethod
    def today(cls):
        return cls(dt.datetime.today())

DateTime.max = DateTime(dt.datetime.max)
DateTime.min = DateTime(dt.datetime.min)
DateTime._null_datetime = object.__new__(DateTime)
DateTime._null_datetime._datetime = None
NullDateTime = DateTime()


class Time(object):
    """
    adds null capable datetime.time constructs
    """

    __slots__ = ['_time']

    def __new__(cls, hour=None, minute=0, second=0, microsecond=0, tzinfo=None):
        """
        hour may be a datetime.time or a str(Time)
        """
        if hour is None:
            return cls._null_time
        nt = object.__new__(cls)
        if isinstance(hour, basestring):
            hour = Time.strptime(hour)
        if isinstance(hour, Time):
            if tzinfo is not None and hour._time.tzinfo:
                raise ValueError('not naive time (tzinfo is already set)')
            nt._time = hour._time.replace(tzinfo=tzinfo)
        elif isinstance(hour, dt.time):
            if tzinfo is not None and hour.tzinfo:
                raise ValueError('not naive time (tzinfo is already set)')
            if tzinfo is None:
                tzinfo = hour.tzinfo
            microsecond = int(hour.microsecond)
            hour, minute, second = hour.hour, hour.minute, hour.second
            nt._time = dt.time(hour, minute, second, microsecond, tzinfo)
        elif hour is not None:
            microsecond = int(microsecond)
            nt._time = dt.time(hour, minute, second, microsecond, tzinfo)
        return nt

    def __add__(self, other):
        if self and isinstance(other, timedeltas):
            t = self._time
            t = dt.datetime(2012, 6, 27, t.hour, t.minute, t.second, t.microsecond)
            t += other
            return Time(t.hour, t.minute, t.second, t.microsecond)
        else:
            return NotImplemented

    def __eq__(self, other):
        if isinstance(other, Time):
            return self._time == other._time
        if isinstance(other, dt.time):
            return (
                    self.hour == other.hour and
                    self.minute == other.minute and
                    self.second == other.second and
                    self.microsecond == int(other.microsecond)
                    )
        if isinstance(other, type(None)):
            return self._time is None
        return NotImplemented

    def __format__(self, spec):
        if self:
            return self._time.__format__(spec)
        return ''

    def __getattr__(self, name):
        if name == '_time':
            raise AttributeError('_time missing!')
        elif self:
            return getattr(self._time, name)
        else:
            raise AttributeError('NullTime object has no attribute %s' % name)

    def __ge__(self, other):
        if self:
            if isinstance(other, dt.time):
                return self._time >= other
            elif isinstance(other, Time):
                if other:
                    return self._time >= other._time
                return False
        else:
            if isinstance(other, dt.time):
                return False
            elif isinstance(other, Time):
                if other:
                    return False
                return True
        return NotImplemented

    def __gt__(self, other):
        if self:
            if isinstance(other, dt.time):
                return self._time > other
            elif isinstance(other, DateTime):
                if other:
                    return self._time > other._time
                return True
        else:
            if isinstance(other, dt.time):
                return False
            elif isinstance(other, Time):
                if other:
                    return False
                return False
        return NotImplemented

    def __hash__(self):
        return self._datetime.__hash__()

    def __le__(self, other):
        if self:
            if isinstance(other, dt.time):
                return self._time <= other
            elif isinstance(other, Time):
                if other:
                    return self._time <= other._time
                return False
        else:
            if isinstance(other, dt.time):
                return True
            elif isinstance(other, Time):
                if other:
                    return True
                return True
        return NotImplemented

    def __lt__(self, other):
        if self:
            if isinstance(other, dt.time):
                return self._time < other
            elif isinstance(other, Time):
                if other:
                    return self._time < other._time
                return False
        else:
            if isinstance(other, dt.time):
                return True
            elif isinstance(other, Time):
                if other:
                    return True
                return False
        return NotImplemented

    def __ne__(self, other):
        if self:
            if isinstance(other, dt.time):
                return self._time != other
            elif isinstance(other, Time):
                if other:
                    return self._time != other._time
                return True
        else:
            if isinstance(other, dt.time):
                return True
            elif isinstance(other, Time):
                if other:
                    return True
                return False
        return NotImplemented

    if PY_VER < (3, 0):
        def __nonzero__(self):
            return self._time is not None
    else:
        def __bool__(self):
            return self._time is not None

    __radd__ = __add__

    def __rsub__(self, other):
        if self and isinstance(other, times):
            t = self._time
            t = dt.datetime(2012, 6, 27, t.hour, t.minute, t.second, t.microsecond)
            other = dt.datetime(2012, 6, 27, other.hour, other.minute, other.second, other.microsecond)
            other -= t
            return TimeDelta(other)
        else:
            return NotImplemented

    def __repr__(self):
        if self:
            if self.tzinfo is None:
                tz = ''
            else:
                diff = self._time.tzinfo.utcoffset(self._time)
                hours, minutes = divmod(diff.days * OD + diff.seconds, OH)
                minus, hours = hours < 0, abs(hours)
                tz = ', tzinfo=<%s %s%02d%02d>' % (self._time.tzinfo.tzname(self._time), ('','-')[minus], hours, minutes)
            return "Time(%d, %d, %d, %d%s)" % (self.hour, self.minute, self.second, self.microsecond, tz)
        else:
            return "Time()"

    def __str__(self):
        if self:
            return unicode(self._time)
        return ""

    def __sub__(self, other):
        if self and isinstance(other, times):
            t = self._time
            t = dt.datetime(2012, 6, 27, t.hour, t.minute, t.second, t.microsecond)
            o = dt.datetime(2012, 6, 27, other.hour, other.minute, other.second, other.microsecond)
            return TimeDelta(t - o)
        elif self and isinstance(other, timedeltas):
            t = self._time
            t = dt.datetime(2012, 6, 27, t.hour, t.minute, t.second, t.microsecond)
            t -= other
            return Time(t.hour, t.minute, t.second, t.microsecond)
        else:
            return NotImplemented

    @classmethod
    def fromfloat(cls, num):
        "2.5 == 2 hours, 30 minutes, 0 seconds, 0 microseconds"
        if num < 0:
            raise ValueError("positive value required (got %r)" % num)
        if num == 0:
            return Time(0)
        hours = int(num)
        if hours:
            num = num % hours
        minutes = int(num * OM)
        if minutes:
            num = num * OM % minutes
        else:
            num = num * OM
        seconds = int(num * OM)
        if seconds:
            num = num * OM % seconds
        else:
            num = num * OM
        microseconds = int(num * MILLION)
        return Time(hours, minutes, seconds, microseconds)

    @staticmethod
    def now(tzinfo=None):
        "only accurate to milliseconds"
        return DateTime.now(tzinfo).timetz()

    def replace(
            self,
            hour=None, minute=None, second=None, microsecond=None, tzinfo=None,
            delta_hour=0, delta_minute=0, delta_second=0, delta_microsecond=0,
        ):
        if not self:
            return Time._null_time
        if tzinfo is None:
            tzinfo = self._time.tzinfo
        old_hour, old_minute, old_second, old_micro = self.hour, self.minute, self.second, self.microsecond
        hour = (old_hour if hour is None else hour) + delta_hour
        minute = (old_minute if minute is None else minute) + delta_minute
        second = (old_second if second is None else second) + delta_second
        microsecond = (old_micro if microsecond is None else microsecond) + delta_microsecond
        while not (0 <= hour < 24) or not (0 <= minute < OM) or not (0 <= second < OM) or not (0 <= microsecond < MILLION):
            while microsecond < 0:
                second -= 1
                microsecond += MILLION
            while second < 0:
                minute -= 1
                second += OM
            while second > 59:
                minute += 1
                second -= OM
            while minute < 0:
                hour -= 1
                minute += OM
            while minute > 59:
                hour += 1
                minute -= OM
            while hour < 0:
                hour += 24
            while hour > 23:
                hour -= 24
        return Time(hour, minute, second, microsecond, tzinfo)

    def strftime(self, format):
        fmt_cls = type(format)
        if self:
            return fmt_cls(self._time.strftime(format))
        return fmt_cls('')

    @classmethod
    def strptime(cls, time_string, format=None):
        if format is not None:
            return cls(*time.strptime(time_string, format)[3:6])
        for format in (
                "%H:%M:%S.%f",
                "%H:%M:%S",
                ):
            try:
                return cls(*time.strptime(time_string, format)[3:6])
            except ValueError:
                pass
        raise ValueError("Unable to convert %r" % time_string)

    def time(self):
        if self:
            return self._time
        return None

    def tofloat(self):
        "returns Time as a float"
        hour = self.hour
        minute = self.minute * (1.0 / OM)
        second = self.second * (1.0 / OH)
        microsecond = self.microsecond * (1.0 / 3600000)
        return hour + minute + second + microsecond

Time.max = Time(dt.time.max)
Time.min = Time(dt.time.min)
Time._null_time = object.__new__(Time)
Time._null_time._time = None
NullTime = Time()


class TimeDelta(object):
    """
    handles repr of negative values sanely
    """

    __slots__ = ['days','seconds','microseconds','_str','_repr','_total_seconds', '_bool']
    time_units = {'w': 7*OD, 'd':OD, 'h':OH, 'm':OM, 's':1}

    def __new__(cls, days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0):
        if isinstance(days, timedeltas):
            if seconds or microseconds or milliseconds or minutes or hours or weeks:
                raise ValueError('cannot specify other arguments when days is a timedelta')
            microseconds = days.microseconds
            seconds = days.seconds
            days = days.days
        elif isinstance(days, basestring):
            if seconds or microseconds or milliseconds or minutes or hours or weeks:
                raise ValueError('cannot specify other arguments when days is a string')
            seconds = cls.time2seconds(days)
            days = 0
        # normalize units
        seconds = (weeks*7+days)*OD + hours*OH + minutes*OM + seconds
        microseconds = milliseconds*10**3 + microseconds
        excess_ms, microseconds = divmod(microseconds, MILLION)
        seconds += excess_ms
        self = object.__new__(cls)
        self._total_seconds = seconds + microseconds*10**-6
        self.days, self.seconds = divmod(seconds, OD)
        self.microseconds = microseconds
        vals = []
        days, seconds = divmod(seconds, OD)
        if days:
            vals.append("days=%d" % days)
        if seconds:
            vals.append("seconds=%d" % seconds)
        if microseconds:
            vals.append("microseconds=%d" % microseconds)
        self._repr = "TimeDelta(%s)" % ', '.join(vals)
        self._str = self.seconds2time(self._total_seconds)
        self._bool = days == 0 and seconds == 0 and microseconds == 0
        return self

    def __add__(self, other):
        if not isinstance(other, moments+timedeltas):
            return NotImplemented
        if isinstance(other, datetimes+dates):
            return other + dt.timedelta(self.days, self.seconds, self.microseconds)
        elif isinstance(other, timedeltas):
            return TimeDelta(
                    days=self.days+other.days,
                    seconds=self.seconds+other.seconds,
                    microseconds=self.microseconds+other.microseconds,
                    )
        elif isinstance(other, times):
            cls = type(other)
            _days, seconds = divmod(self.seconds, OD)
            nt = Time(other).replace(delta_second=seconds, delta_microsecond=self.microseconds)
            return cls(nt.hour, nt.minute, nt.second, nt.microsecond, nt.tzinfo)
        else:
            raise TypeError('unhandled type %r [%r]' % (type(other), other))

    __radd__ = __add__

    def __truediv__(self, other):
        try:
            if isinstance(other, timedeltas):
                other = (other.days*OD + other.seconds) * MILLION + other.microseconds
            else:
                other *= MILLION
            return ((self.days*OD + self.seconds) * MILLION + self.microseconds) / other
        except (ValueError, TypeError):
            return NotImplemented

    if PY_VER < (3, 0):
        __div__ = __truediv__

    def __divmod__(self, other):
        try:
            total = (self.days*OD + self.seconds) * MILLION + self.microseconds
            if isinstance(other, timedeltas):
                other = (other.days*OD + other.seconds) * MILLION + other.microseconds
            else:
                other *= MILLION
            q = total // other
            s, m = divmod(total-q*other, MILLION)
            r = TimeDelta(seconds=s, microseconds=m)
            return q, r
        except (ValueError, TypeError):
            return NotImplemented

    def __eq__(self, other):
        if not isinstance(other, timedeltas):
            return NotImplemented
        return self.days == other.days and self.seconds == other.seconds and self.microseconds == int(other.microseconds)

    def __floordiv__(self, other):
        try:
            if isinstance(other, timedeltas):
                other = (other.days*OD + other.seconds) * MILLION + other.microseconds
            else:
                other *= MILLION
            return ((self.days*OD + self.seconds) * MILLION + self.microseconds) // other
        except (ValueError, TypeError):
            return NotImplemented

    def __ge__(self, other):
        if not isinstance(other, timedeltas):
            return NotImplemented
        if self.days > other.days:
            return True
        elif self.days == other.days:
            if self.seconds > other.seconds:
                return True
            elif self.seconds == other.seconds:
                return self.microseconds >= other.microseconds
        return False

    def __gt__(self, other):
        if not isinstance(other, timedeltas):
            return NotImplemented
        if self.days > other.days:
            return True
        elif self.days == other.days:
            if self.seconds > other.seconds:
                return True
            elif self.seconds == other.seconds:
                return self.microseconds > other.microseconds
        return False

    def __hash__(self):
        return self.seconds + self.microseconds

    def __le__(self, other):
        if not isinstance(other, timedeltas):
            return NotImplemented
        if self.days < other.days:
            return True
        elif self.days == other.days:
            if self.seconds < other.seconds:
                return True
            elif self.seconds == other.seconds:
                return self.microseconds <= other.microseconds
        return False

    def __lt__(self, other):
        if not isinstance(other, timedeltas):
            return NotImplemented
        if self.days < other.days:
            return True
        elif self.days == other.days:
            if self.seconds < other.seconds:
                return True
            elif self.seconds == other.seconds:
                return self.microseconds < other.microseconds
        return False

    def __mod__(self, other):
        try:
            return self.__divmod__(other)[1]
        except TypeError:
            return NotImplemented

    def __mul__(self, other):
        try:
            return TimeDelta(self.days*other, self.seconds*other, self.microseconds*other)
        except (ValueError, TypeError):
            return NotImplemented

    __rmul__ = __mul__

    def __ne__(self, other):
        if not isinstance(other, timedeltas):
            return NotImplemented
        return self.days != other.days or self.seconds != other.seconds or self.microseconds != int(other.microseconds)

    if PY_VER < (3, 0):
        def __nonzero__(self):
            return self._bool
    else:
        def __bool__(self):
            return self._bool

    def __rtruediv__(self, other):
        try:
            if isinstance(other, timedeltas):
                other = (other.days*OD + other.seconds) * MILLION + other.microseconds
            else:
                other *= MILLION
            return other / ((self.days*OD + self.seconds) * MILLION + self.microseconds)
        except (ValueError, TypeError):
            return NotImplemented

    if PY_VER < (3, 0):
        __rdiv__ = __rtruediv__

    def __rdivmod__(self, other):
        try:
            total = (self.days*OD + self.seconds) * MILLION + self.microseconds
            if isinstance(other, timedeltas):
                other = (other.days*OD + other.seconds) * MILLION + other.microseconds
            else:
                other *= MILLION
            q = other // total
            s, m = divmod(other-q*total, MILLION)
            r = TimeDelta(seconds=s, microseconds=m)
            return q, r
        except (ValueError, TypeError):
            return NotImplemented

    def __rfloordiv__(self, other):
        try:
            if isinstance(other, timedeltas):
                other = (other.days*OD + other.seconds) * MILLION + other.microseconds
            else:
                other *= MILLION
            return other // ((self.days*OD + self.seconds) * MILLION + self.microseconds)
        except (ValueError, TypeError):
            return NotImplemented

    def __repr__(self):
        return self._repr

    def __rsub__(self, other):
        if isinstance(other, timedeltas):
            return TimeDelta(other.days-self.days, other.seconds-self.seconds, int(other.microseconds)-self.microseconds)
        elif isinstance(other, moments):
            return other - dt.timedelta(self.days, self.seconds, self.microseconds)
        else:
            return NotImplemented

    def __str__(self):
        return self._str

    def __sub__(self, other):
        if isinstance(other, timedeltas):
            return TimeDelta(other.days-self.days, other.seconds-self.seconds, int(other.microseconds)-self.microseconds)
        else:
            return NotImplemented

    def seconds2time(self, seconds):
        if seconds < 0:
            result = '-'
            seconds *= -1
        else:
            result = ''
        use_if_empty = False
        for unit in 'ds':
            size = self.time_units[unit]
            if seconds < size and not use_if_empty:
                continue
            use_if_empty = True
            amount, seconds = divmod(seconds, size)
            result = ('%s %2i%s' % (result, amount, unit)).strip()
            # if seconds == 0:
            #     break
        return result or ' 0s'

    def time2seconds(self, time):
        "convert time to seconds (e.g. 2m -> 120)"
        # if all digits, must be seconds already
        if not time:
            return 0
        elif isinstance(time, baseinteger):
            return time
        text = time
        if text[0] == '-':
            sign = -1
            text = text[1:]
        else:
            sign = +1
        text = ''.join(text.split())
        if text.isdigit():
            return sign * int(text)
        moment = 0
        digits = []
        for c in text:
            if c.isdigit():
                digits.append(c)
                continue
            number = int(''.join(digits))
            c = c.lower()
            if c not in ('wdhms'):
                raise ValueError('invalid time: %r' % time)
            moment += self.time_units[c] * number
            digits = []
        else:
            if digits:
                # didn't specify a unit, abort
                raise ValueError('missing trailing time unit of w, d, h, m, or s in %r' % time)
        return moment

    def total_seconds(self):
        return self._total_seconds

dates = Date, dt.date
times = Time, dt.time
datetimes = DateTime, dt.datetime
moments = dates + times + datetimes
timedeltas = TimeDelta, dt.timedelta


# add xmlrpc support
if PY_VER < (3, 0):
    from xmlrpclib import Marshaller
else:
    from xmlrpc.client import Marshaller

# DateTime is transmitted as UTC if aware, local if naive
Marshaller.dispatch[DateTime] = lambda s, dt, w: w(
        '<value><dateTime.iso8601>'
        '%04d%02d%02dT%02d:%02d:%02d'
        '</dateTime.iso8601></value>\n'
            % dt.utctimetuple()[:6])
del Marshaller

