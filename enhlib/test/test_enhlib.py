from __future__ import print_function

from .. import *
from ..contextlib import suppress
from ..csv import CSV
from ..itertools import all_equal, xrange, zip
from ..text import translator
from ..types import Logical, Null, Truth, Falsth, Unknown
from ..datetime import Date, Time, DateTime, TimeDelta, NullDate, NullDateTime, NullTime
from ..stdlib import datetime as dt
import re
import sys
import unittest

try:
    from string import letters, digits, lowercase, uppercase
except ImportError:
    from string import ascii_letters as letters, digits, ascii_lowercase as lowercase, ascii_uppercase as uppercase

try:
    import pytz
except ImportError:
    pytz = None

try:
    from enum import Enum
except ImportError:
    try:
        from aenum import Enum
    except ImportError:
        Enum = None

## globals

class TestCase(unittest.TestCase):
    def __init__(self, *args, **kwds):
        regex = getattr(self, 'assertRaisesRegex', None)
        if regex is None:
            self.assertRaisesRegex = getattr(self, 'assertRaisesRegexp')
        super(TestCase, self).__init__(*args, **kwds)



## tests

class Test_all_equal(TestCase):
    #
    def test_simple_equal(self):
        for items in (
                (1, 1, 1, 1, 1),
                (21, 21, 21),
                [827, 827, 827, 827, 827],
                [None, None],
                [],
                ):
            self.assertTrue(all_equal(items), '%r not all equal?' % (items, ))

    def test_simple_not_equal(self):
        for items in (
                (1, 1, 1, 1, 11),
                (21, 2, 21),
                [3, 827, 827, 827, 827],
                [None, None, False],
                ):
            self.assertFalse(all_equal(items), '%r all equal?' % (items, ))

    def test_function_equal(self):
        for items, func in (
                ((10, 12, 26, 4, 100), lambda x: x % 2 == 0),
                (('abc', 'def', 'ghi'), lambda x: len(x) == 3),
                ([827, 27, 87, 71, 99], lambda x: x % 2 == 1),
                ([None, None], lambda x: x is None),
                ([], lambda x: x is True),
                ):
            self.assertTrue(all_equal(items, func), '%r not all equal?' % (items, ))

    def test_function_not_equal(self):
        for items, func in (
                ((10, 12, 26, 4, 101), lambda x: x % 2 == 0),
                (('abc', 'defg', 'hij'), lambda x: len(x) == 3),
                ([82, 27, 87, 71, 99], lambda x: x % 2 == 1),
                ([None, None, True], lambda x: x is None),
                ):
            self.assertFalse(all_equal(items, func), '%r all equal?' % (items, ))

class Test_suppress(TestCase):
    #
    def test_no_exception(self):
        with suppress(ValueError):
            self.assertEqual(pow(2, 5), 32)

    def test_exact_exception(self):
        with suppress(TypeError):
            len(5)
        with self.assertRaises(AttributeError):
            with suppress(TypeError):
                None.not_here

    def test_multiple_exception_args(self):
        with suppress(ZeroDivisionError, TypeError):
            len(5)
        with suppress(ZeroDivisionError, TypeError):
            5 / 0
        with self.assertRaises(AttributeError):
            with suppress(ZeroDivisionError, TypeError):
                None.not_here

    def test_exception_hierarchy(self):
        with suppress(LookupError):
            'Hello'[50]

class Test_translator(TestCase):
    #
    def test_keep(self):
        alpha = translator(keep=letters)
        self.assertEqual(alpha('ethan7'), 'ethan')
        self.assertEqual(alpha('1234z'), 'z')
        self.assertEqual(alpha('ABCdef'), 'ABCdef')
        self.assertEqual(alpha('1234'), '')

    def test_delete(self):
        no_alpha = translator(delete=letters)
        self.assertEqual(no_alpha('ethan7'), '7')
        self.assertEqual(no_alpha('1234z'), '1234')
        self.assertEqual(no_alpha('ABCdef'), '')
        self.assertEqual(no_alpha('1234'), '1234')
        self.assertEqual(no_alpha('+|%.'), '+|%.')

    def test_to_keep(self):
        replace = translator(to=' ', keep=letters)
        self.assertEqual(replace('ethan7'), 'ethan ')
        self.assertEqual(replace('1234z'), '    z')
        self.assertEqual(replace('ABCdef'), 'ABCdef')
        self.assertEqual(replace('1234'), '    ')
        self.assertEqual(replace('ABC-def'), 'ABC def')

    def test_to_keep_compress(self):
        replace = translator(to=' ', keep=letters, compress=True)
        self.assertEqual(replace('ethan7'), 'ethan')
        self.assertEqual(replace('1234z'), 'z')
        self.assertEqual(replace('ABCdef'), 'ABCdef')
        self.assertEqual(replace('1234'), '')
        self.assertEqual(replace('ABC-def'), 'ABC def')
        self.assertEqual(replace('ABC-def//GhI'), 'ABC def GhI')

    def test_frm_to(self):
        upper = translator(frm=lowercase, to=uppercase)
        self.assertEqual(upper('ethan7'), 'ETHAN7')
        self.assertEqual(upper('1234z'), '1234Z')
        self.assertEqual(upper('ABCdef'), 'ABCDEF')
        self.assertEqual(upper('1234'), '1234')
        self.assertEqual(upper('ABC-def'), 'ABC-DEF')
        self.assertEqual(upper('ABC-def//GhI'), 'ABC-DEF//GHI')

    def test_frm_to_delete(self):
        upper = translator(frm=lowercase, to=uppercase, delete=digits)
        self.assertEqual(upper('ethan7'), 'ETHAN')
        self.assertEqual(upper('1234z'), 'Z')
        self.assertEqual(upper('ABCdef'), 'ABCDEF')
        self.assertEqual(upper('1234'), '')
        self.assertEqual(upper('ABC-def'), 'ABC-DEF')
        self.assertEqual(upper('ABC-def//789...GhI'), 'ABC-DEF//...GHI')


class Test_xrange(TestCase):
    #
    def test_int_iter_forwards(self):
        self.assertEqual(
                list(range(10)),
                list(xrange(10)))
        self.assertEqual(
                list(range(0, 10)),
                list(xrange(0, 10)))
        self.assertEqual(
                list(range(0, 10, 1)),
                list(xrange(0, 10, 1)))
        self.assertEqual(
                list(range(0, 10, 1)),
                list(xrange(0, count=10)))
        self.assertEqual(
                list(range(0, 10, 1)),
                list(xrange(10, step=lambda s, i, v: v+1)))
        self.assertEqual(
                list(range(0, 10, 1)),
                list(xrange(10, step=lambda s, i, v: v+1)))
        self.assertEqual(
                list(range(5, 15)),
                list(xrange(5, count=10)))
        self.assertEqual(
                list(range(-10, 0)),
                list(xrange(-10, 0)))
        self.assertEqual(
                list(range(-9, 1)),
                list(xrange(-9, 1)))
        self.assertEqual(
                list(range(-20, 20, 1)),
                list(xrange(-20, 20, 1)))
        self.assertEqual(
                list(range(-20, 20, 2)),
                list(xrange(-20, 20, 2)))
        self.assertEqual(
                list(range(-20, 20, 3)),
                list(xrange(-20, 20, 3)))
        self.assertEqual(
                list(range(-20, 20, 4)),
                list(xrange(-20, 20, 4)))
        self.assertEqual(
                list(range(-20, 20, 5)),
                list(xrange(-20, 20, 5)))

    def test_int_iter_backwards(self):
        self.assertEqual(
                list(range(9, -1, -1)),
                list(xrange(9, -1, -1)))
        self.assertEqual(
                list(range(9, -9, -1)),
                list(xrange(9, -9, -1)))
        self.assertEqual(
                list(range(9, -9, -2)),
                list(xrange(9, -9, -2)))
        self.assertEqual(
                list(range(9, -9, -3)),
                list(xrange(9, -9, -3)))
        self.assertEqual(
                list(range(9, 0, -1)),
                list(xrange(9, 0, -1)))
        self.assertEqual(
                list(range(9, -1, -1)),
                list(xrange(9, -1, step=-1, count=10)))

    def test_int_containment(self):
        robj = xrange(10)
        for i in range(10):
            self.assertTrue(i in robj, '%d not in %r' % (i, robj))
        self.assertFalse(-1 in robj)
        self.assertFalse(10 in robj)
        self.assertFalse(5.23 in robj)

    def test_float_iter(self):
        floats = [float(i) for i in range(100)]
        self.assertEqual(
                floats,
                list(xrange(100.0, epsilon=0.5)))
        self.assertEqual(
                floats,
                list(xrange(0, 100.0, epsilon=0.5)))
        self.assertEqual(
                floats,
                list(xrange(0, 100.0, 1.0, epsilon=0.5)))
        self.assertEqual(
                floats,
                list(xrange(100.0, step=lambda s, i, v: v + 1.0, epsilon=0.5)))
        self.assertEqual(
                floats,
                list(xrange(100.0, step=lambda s, i, v: s + i * 1.0, epsilon=0.5)))
        self.assertEqual(
                floats,
                list(xrange(0.0, count=100, epsilon=0.5)),
                repr(xrange(0.0, count=100, epsilon=0.5)))
        self.assertEqual(
                [0.3, 0.6],
                list(xrange(0.3, 0.9, 0.3, epsilon=0.15)))
        self.assertEqual(
                [0.4, 0.8],
                list(xrange(0.4, 1.2, 0.4, epsilon=0.2)))

    def test_float_iter_backwards(self):
        floats = [float(i) for i in range(99, -1, -1)]
        self.assertEqual(
                floats,
                list(xrange(99.0, -1, -1, epsilon=0.5)))
        self.assertEqual(
                floats,
                list(xrange(99.0, step=lambda s, i, v: v - 1.0, count=100, epsilon=0.5)))
        self.assertEqual(
                [0.6, 0.3],
                list(xrange(0.6, 0.0, -0.3, epsilon=0.15)))
        self.assertEqual(
                [0.8, 0.4]
                , list(xrange(0.8, 0.0, -0.4, epsilon=0.2)))

    def test_float_containment(self):
        robj = xrange(10000.0, epsilon=0.5)
        for i in range(0, 10000, 100):
            i = float(i)
            self.assertTrue(i in robj, '%s not in %r' % (i, robj))
        self.assertFalse(0.000001 in robj)
        self.assertFalse(1000000000.0 in robj)
        self.assertFalse(50.23 in robj)

    def test_date_iter(self):
        ONE_DAY = dt.timedelta(1)
        robj = xrange(dt.date(2014, 1, 1), step=ONE_DAY, count=31)
        day1 = dt.date(2014, 1, 1)
        riter = iter(robj)
        for i in range(31):
            day = day1 + i * ONE_DAY
            rday = next(riter)
            self.assertEqual(day, rday)
            self.assertTrue(day in robj)
        self.assertRaises(StopIteration, next, riter)
        self.assertFalse(day + ONE_DAY in robj)

    def test_enhlib_date_iter(self):
        ONE_DAY = TimeDelta(1)
        robj = xrange(Date(2014, 1, 1), step=ONE_DAY, count=31)
        day1 = Date(2014, 1, 1)
        riter = iter(robj)
        for i in range(31):
            day = day1 + i * ONE_DAY
            rday = next(riter)
            self.assertEqual(day, rday)
            self.assertTrue(day in robj)
        self.assertRaises(StopIteration, next, riter)
        self.assertFalse(day + ONE_DAY in robj)

    def test_fraction_iter(self):
        from fractions import Fraction as F
        f = xrange(F(5, 10), count=3)
        self.assertEqual([F(5, 10), F(15, 10), F(25, 10)], list(f))





class Test_datetime(TestCase):
    "Testing Date, Time, DateTime, TimeDelta"

    def test_date_creation(self):
        self.assertEqual(Date(), NullDate)
        self.assertEqual(Date.fromymd('        '), NullDate)
        self.assertEqual(Date.fromymd('00000000'), NullDate)
        self.assertEqual(Date.fromordinal(0), NullDate)
        self.assertEqual(Date.today(), dt.date.today())
        self.assertEqual(Date.max, dt.date.max)
        self.assertEqual(Date.min, dt.date.min)
        self.assertEqual(Date(2018, 5, 21), dt.date(2018, 5, 21))
        self.assertEqual(Date.strptime('2018-01-01'), dt.date(2018, 1, 1))
        self.assertRaises(ValueError, Date.fromymd, '00000')
        self.assertRaises(ValueError, Date, 0, 0, 0)

    def test_date_compare(self):
        nodate1 = Date()
        nodate2 = Date()
        date1 = Date.fromordinal(1000)
        date2 = Date.fromordinal(2000)
        date3 = Date.fromordinal(3000)
        self.compareTimes(nodate1, nodate2, date1, date2, date3)

    def test_datetime_creation(self):
        self.assertEqual(DateTime(), NullDateTime)
        self.assertEqual(DateTime.fromordinal(0), NullDateTime)
        self.assertTrue(DateTime.today())
        self.assertEqual(DateTime.max, dt.datetime.max)
        self.assertEqual(DateTime.min, dt.datetime.min)
        self.assertEqual(DateTime(2018, 5, 21, 19, 17, 16), dt.datetime(2018, 5, 21, 19, 17 ,16))
        self.assertEqual(DateTime.strptime('2018-01-01 19:17:16'), dt.datetime(2018, 1, 1, 19, 17, 16))

    def test_datetime_compare(self):
        nodatetime1 = DateTime()
        nodatetime2 = DateTime()
        datetime1 = DateTime.fromordinal(1000)
        datetime2 = DateTime.fromordinal(20000)
        datetime3 = DateTime.fromordinal(300000)
        self.compareTimes(nodatetime1, nodatetime2, datetime1, datetime2, datetime3)

    def test_time_creation(self):
        self.assertEqual(Time(), NullTime)
        self.assertEqual(Time.max, dt.time.max)
        self.assertEqual(Time.min, dt.time.min)
        self.assertEqual(Time(19, 17, 16), dt.time(19, 17 ,16))
        self.assertEqual(Time.strptime('19:17:16'), dt.time(19, 17, 16))

    def test_time_compare(self):
        notime1 = Time()
        notime2 = Time()
        time1 = Time.fromfloat(7.75)
        time2 = Time.fromfloat(9.5)
        time3 = Time.fromfloat(16.25)
        self.compareTimes(notime1, notime2, time1, time2, time3)

    @unittest.skipIf(pytz is None, 'pytz not installed')
    def test_datetime_tz(self):
        pst = pytz.timezone('America/Los_Angeles')
        mst = pytz.timezone('America/Boise')
        cst = pytz.timezone('America/Chicago')
        est = pytz.timezone('America/New_York')
        utc = pytz.timezone('UTC')
        #
        pdt = DateTime(2018, 5, 20, 5, 41, 33, tzinfo=pst)
        mdt = DateTime(2018, 5, 20, 6, 41, 33, tzinfo=mst)
        cdt = DateTime(2018, 5, 20, 7, 41, 33, tzinfo=cst)
        edt = DateTime(2018, 5, 20, 8, 41, 33, tzinfo=est)
        udt = DateTime(2018, 5, 20, 12, 41, 33, tzinfo=utc)
        self.assertTrue(pdt == mdt == cdt == edt == udt)
        #
        dup1 = DateTime.combine(pdt.date(), mdt.timetz())
        dup2 = DateTime.combine(cdt.date(), Time(5, 41, 33, tzinfo=pst))
        self.assertTrue(dup1 == dup2 == udt)
        #
        udt2 = DateTime(2018, 5, 20, 13, 41, 33, tzinfo=utc)
        mdt2 = mdt.replace(tzinfo=pst)
        self.assertTrue(mdt2 == udt2, "%r != %r" % (mdt2, udt2))
        #
        with self.assertRaisesRegex(ValueError, 'not naive datetime'):
            DateTime(pdt, tzinfo=mst)
        with self.assertRaisesRegex(ValueError, 'not naive datetime'):
            DateTime(dt.datetime(2018, 5, 27, 15, 57, 11, tzinfo=pst), tzinfo=pst)
        with self.assertRaisesRegex(ValueError, 'not naive time'):
            Time(pdt.timetz(), tzinfo=mst)
        with self.assertRaisesRegex(ValueError, 'not naive time'):
            Time(dt.time(15, 58, 59, tzinfo=mst), tzinfo=mst)
        #
        if PY_VER < (3, 0):
            from xmlrpclib import Marshaller, loads
        else:
            from xmlrpc.client import Marshaller, loads
        self.assertEqual(
                udt.utctimetuple(),
                loads(Marshaller().dumps([pdt]), use_datetime=True)[0][0].utctimetuple(),
                )
        #
        self.assertEqual(
                pdt,
                DateTime.combine(Date(2018, 5, 20), Time(5, 41, 33), tzinfo=pst),
                )

    def test_arithmetic(self):
        one_day = dt.timedelta(1)
        a_day = Date(1970, 5, 20)
        self.assertEqual(a_day + one_day, Date(1970, 5, 21))
        self.assertEqual(a_day - one_day, Date(1970, 5, 19))
        self.assertEqual(dt.date(1970, 5, 21) - a_day, one_day)
        a_time = Time(12)
        one_second = dt.timedelta(0, 1, 0)
        self.assertEqual(a_time + one_second, Time(12, 0, 1))
        self.assertEqual(a_time - one_second, Time(11, 59, 59))
        self.assertEqual(dt.time(12, 0, 1) - a_time, one_second)
        an_appt = DateTime(2012, 4, 15, 12, 30, 00)
        displacement = dt.timedelta(1, 60*60*2+60*15)
        self.assertEqual(an_appt + displacement, DateTime(2012, 4, 16, 14, 45, 0))
        self.assertEqual(an_appt - displacement, DateTime(2012, 4, 14, 10, 15, 0))
        self.assertEqual(dt.datetime(2012, 4, 16, 14, 45, 0) - an_appt, displacement)
        #
        one_day = TimeDelta(1)
        a_day = dt.date(1970, 5, 20)
        self.assertEqual(a_day + one_day, dt.date(1970, 5, 21))
        self.assertTrue(type(a_day + one_day) is dt.date)
        self.assertEqual(a_day - one_day, dt.date(1970, 5, 19))
        self.assertTrue(type(a_day - one_day) is dt.date)
        self.assertEqual(TimeDelta(dt.date(1970, 5, 21) - a_day), one_day)
        an_appt = dt.datetime(2012, 4, 15, 12, 30, 00)
        displacement = TimeDelta(1, 60*60*2+60*15)
        self.assertEqual(an_appt + displacement, dt.datetime(2012, 4, 16, 14, 45, 0))
        self.assertTrue(type(an_appt + displacement) is dt.datetime)
        self.assertEqual(an_appt - displacement, dt.datetime(2012, 4, 14, 10, 15, 0))
        self.assertTrue(type(an_appt - displacement) is dt.datetime)
        self.assertEqual(TimeDelta(dt.datetime(2012, 4, 16, 14, 45, 0) - an_appt), displacement)
        #
        one_day = TimeDelta(1)
        a_day = Date(1970, 5, 20)
        self.assertEqual(a_day + one_day, Date(1970, 5, 21))
        self.assertEqual(a_day - one_day, Date(1970, 5, 19))
        self.assertEqual(dt.date(1970, 5, 21) - a_day, one_day)
        a_time = Time(12)
        one_second = TimeDelta(0, 1, 0)
        self.assertEqual(a_time + one_second, Time(12, 0, 1))
        self.assertEqual(a_time - one_second, Time(11, 59, 59))
        self.assertEqual(dt.time(12, 0, 1) - a_time, one_second)
        an_appt = DateTime(2012, 4, 15, 12, 30, 00)
        displacement = TimeDelta(1, 60*60*2+60*15)
        self.assertEqual(an_appt + displacement, DateTime(2012, 4, 16, 14, 45, 0))
        self.assertEqual(an_appt - displacement, DateTime(2012, 4, 14, 10, 15, 0))
        self.assertEqual(dt.datetime(2012, 4, 16, 14, 45, 0) - an_appt, displacement)

    def test_arithmetic_timedelta_1(self):
        one_day = dt.timedelta(1)
        un_dia = TimeDelta(1)
        one_hour = dt.timedelta(seconds=60*60)
        una_hora = TimeDelta(seconds=60*60)
        zero = dt.timedelta(0)
        cero = TimeDelta(0)
        #
        self.assertEqual(one_hour - una_hora, zero)
        self.assertEqual(one_hour - una_hora, cero)
        self.assertEqual(una_hora - one_hour, zero)
        self.assertEqual(una_hora - one_hour, cero)
        #
        self.assertEqual(un_dia/one_hour, 24)
        self.assertEqual(un_dia/una_hora, 24)
        self.assertEqual(un_dia//one_hour, 24)
        self.assertEqual(un_dia//una_hora, 24)
        #
        self.assertEqual((one_day+una_hora)/one_hour, 25)
        self.assertEqual((one_day+una_hora)/una_hora, 25)
        self.assertEqual((un_dia+one_hour)/one_hour, 25)
        self.assertEqual((un_dia+una_hora)/one_hour, 25)
        self.assertEqual((un_dia+one_hour)/una_hora, 25)
        self.assertEqual((un_dia+una_hora)/una_hora, 25)
        #
        self.assertEqual((one_day+una_hora)//one_hour, 25)
        self.assertEqual((one_day+una_hora)//una_hora, 25)
        self.assertEqual((un_dia+one_hour)//one_hour, 25)
        self.assertEqual((un_dia+una_hora)//one_hour, 25)
        self.assertEqual((un_dia+one_hour)//una_hora, 25)
        self.assertEqual((un_dia+una_hora)//una_hora, 25)
        #
        self.assertEqual(un_dia/24, 3600)
        self.assertEqual((un_dia+una_hora) / 25, 3600)
        self.assertEqual((un_dia+una_hora) % (24*60*60), una_hora)
        self.assertEqual(divmod(un_dia, una_hora), (24, cero))
        self.assertEqual(divmod((un_dia+una_hora), 24*60*60), (1, una_hora))

    @unittest.skipIf(PY_VER < (3, 15), 'datetime.timedelta does not play nice')
    def test_arithmetic_timedelta_2(self):
        one_day = dt.timedelta(1)
        un_dia = TimeDelta(1)
        one_hour = dt.timedelta(seconds=60*60)
        una_hora = TimeDelta(seconds=60*60)
        zero = dt.timedelta(0)
        cero = TimeDelta(0)
        #
        self.assertEqual(one_hour, una_hora)
        self.assertEqual(one_hour - one_hour, cero)
        self.assertEqual(one_day/una_hora, 24)
        self.assertEqual(one_day//una_hora, 24)
        self.assertEqual((one_day+one_hour)/una_hora, 25)
        self.assertEqual((one_day+one_hour)//una_hora, 25)


    def test_none_compare(self):
        empty_date = Date()
        empty_time = Time()
        empty_datetime = DateTime()
        self.assertEqual(empty_date, None)
        self.assertEqual(empty_time, None)
        self.assertEqual(empty_datetime, None)

    def test_singletons(self):
        empty_date = Date()
        empty_time = Time()
        empty_datetime = DateTime()
        self.assertTrue(empty_date is NullDate)
        self.assertTrue(empty_time is NullTime)
        self.assertTrue(empty_datetime is NullDateTime)

    def test_boolean_value(self):
        empty_date = Date()
        empty_time = Time()
        empty_datetime = DateTime()
        self.assertEqual(bool(empty_date), False)
        self.assertEqual(bool(empty_time), False)
        self.assertEqual(bool(empty_datetime), False)
        actual_date = Date.today()
        actual_time = Time.now()
        actual_datetime = DateTime.now()
        self.assertEqual(bool(actual_date), True)
        self.assertEqual(bool(actual_time), True)
        self.assertEqual(bool(actual_datetime), True)

    def compareTimes(self, empty1, empty2, uno, dos, tres):
        self.assertTrue(empty1 is empty2)
        self.assertTrue(empty1 < uno, '%r is not less than %r' % (empty1, uno))
        self.assertFalse(empty1 > uno, '%r is less than %r' % (empty1, uno))
        self.assertTrue(uno > empty1, '%r is not greater than %r' % (empty1, uno))
        self.assertFalse(uno < empty1, '%r is greater than %r' % (empty1, uno))
        self.assertEqual(uno < dos, True)
        self.assertEqual(uno <= dos, True)
        self.assertEqual(dos <= dos, True)
        self.assertEqual(dos <= tres, True)
        self.assertEqual(dos < tres, True)
        self.assertEqual(tres <= tres, True)
        self.assertEqual(uno == uno, True)
        self.assertEqual(dos == dos, True)
        self.assertEqual(tres == tres, True)
        self.assertEqual(uno != dos, True)
        self.assertEqual(dos != tres, True)
        self.assertEqual(tres != uno, True)
        self.assertEqual(tres >= tres, True)
        self.assertEqual(tres > dos, True)
        self.assertEqual(dos >= dos, True)
        self.assertEqual(dos >= uno, True)
        self.assertEqual(dos > uno, True)
        self.assertEqual(uno >= uno, True)
        self.assertEqual(uno >= dos, False)
        self.assertEqual(uno >= tres, False)
        self.assertEqual(dos >= tres, False)
        self.assertEqual(tres <= dos, False)
        self.assertEqual(tres <= uno, False)
        self.assertEqual(tres < tres, False)
        self.assertEqual(tres < dos, False)
        self.assertEqual(tres < uno, False)
        self.assertEqual(dos < dos, False)
        self.assertEqual(dos < uno, False)
        self.assertEqual(uno < uno, False)
        self.assertEqual(uno == dos, False)
        self.assertEqual(uno == tres, False)
        self.assertEqual(dos == uno, False)
        self.assertEqual(dos == tres, False)
        self.assertEqual(tres == uno, False)
        self.assertEqual(tres == dos, False)
        self.assertEqual(uno != uno, False)
        self.assertEqual(dos != dos, False)
        self.assertEqual(tres != tres, False)


class Test_collections(TestCase):
    #
    def test_basics(self):
        from .. import collections
        collections.OrderedDict

    def test_fifo(self):
        from ..collections import fifo
        self.assertEqual(list(fifo()), [])
        self.assertEqual(list(fifo([1,2,3])), [1,2,3])
        huh = fifo([1,2,3])
        huh.append(4)
        self.assertEqual(list(huh), [1,2,3,4])
        self.assertEqual(list(huh), [])
        huh = fifo([1,2,3])
        huh.pop()
        self.assertEqual(list(huh), [2,3])
        self.assertEqual(list(huh), [])
        self.assertRaisesRegex(IndexError, 'pop from empty list', fifo().pop)


class Test_contextlib(TestCase):
    #
    def test_basics(self):
        from .. import contextlib
        contextlib.suppress


class Test_csv(TestCase):
    #
    def test_plain_data_types(self):
        csv = CSV('test.csv', mode='w')
        data_line = True, False, 7.9, 'hello!', dt.date(2025, 5, 20)
        csv_line = csv.to_csv(*data_line)
        self.assertEqual(csv_line, """t,f,7.9,"hello!",2025-05-20""")
        self.assertEqual(csv.from_csv(csv_line), data_line)

    def test_enhlib_data_types(self):
        csv = CSV('test.csv', mode='w')
        data_line = Logical(True), Logical(False), 7.9, 'hello!', Date(2025, 5, 20)
        csv_line = csv.to_csv(*data_line)
        self.assertEqual(csv_line, """t,f,7.9,"hello!",2025-05-20""")
        self.assertEqual(csv.from_csv(csv_line), data_line)

    def test_custom_data_types(self):
        class Custom(object):
            def __init__(self, value):
                self.value = value
            def __repr__(self):
                return ('Custom(%r)' % self.value)
            def __eq__(self, other):
                if isinstance(other, self.__class__):
                    return self.value == other.value
                return NotImplemented
        #
        def test_custom(text):
            return bool(re.match(r'^Custom[(][^)]*[)]$', text))
        def convert_custom(row, text):
            value ,= re.match(r'^Custom[(]([^)]*)[)]$', text).groups()
            return Custom(eval(value))
        #
        csv = CSV('test.csv', mode='w', custom_types=((test_custom, convert_custom), ))
        data_line = True, False, Custom(7.9), 'hello!', dt.date(2025, 5, 20)
        csv_line = csv.to_csv(*data_line)
        self.assertEqual(csv_line, """t,f,Custom(7.9),"hello!",2025-05-20""")
        self.assertEqual(csv.from_csv(csv_line), data_line)


class Test_functools(TestCase):
    #
    def test_basics(self):
        from .. import functools
        functools.simplegeneric


class Test_itertools(TestCase):
    #
    def test_basics(self):
        from .. import itertools
        itertools.all_equal
        itertools.grouped
        itertools.grouped_by_column


class Test_random(TestCase):
    #
    def test_basics(self):
        from .. import random
        random.TinyRand


class Test_text(TestCase):
     #
     def test_basics(self):
         from .. import text
         text.translator


class Test_types(TestCase):
    #
    def test_basics(self):
        from .. import types
        types.MISSING


class Test_zip(TestCase):
    #
    def test_equal_2(self):
        self.assertEqual(
                list(zip(range(5), range(5, 10))),
                [(0, 5), (1, 6), (2, 7), (3, 8), (4, 9)],
                )
    #
    def test_equal_3(self):
        self.assertEqual(
                list(zip(range(5), range(5, 10), range(10, 15))),
                [(0, 5, 10), (1, 6, 11), (2, 7, 12), (3, 8, 13), (4, 9, 14)],
                )
    #
    def test_no_valueerror(self):
        self.assertEqual(
                list(zip(range(4), range(5, 10))),
                [(0, 5), (1, 6), (2, 7), (3, 8)],
                )
    #
    def test_valueerror(self):
        with self.assertRaisesRegex(ValueError, 'zip argument 1 is too short'):
            list(zip(range(4), range(5, 10), strict=True))
    #
    def test_fill(self):
        self.assertEqual(
                list(zip(range(5), range(5, 10), fillvalue=0)),
                [(0, 5), (1, 6), (2, 7), (3, 8), (4, 9)],
                )
        self.assertEqual(
                list(zip(range(5), range(5, 10), range(10, 15), fillvalue=0)),
                [(0, 5, 10), (1, 6, 11), (2, 7, 12), (3, 8, 13), (4, 9, 14)],
                )
        self.assertEqual(
                list(zip(range(5), range(5, 8), fillvalue=0)),
                [(0, 5), (1, 6), (2, 7), (3, 0), (4, 0)],
                )
        self.assertEqual(
                list(zip(range(5), range(5, 8), range(10, 11), fillvalue=0)),
                [(0, 5, 10), (1, 6, 0), (2, 7, 0), (3, 0, 0), (4, 0, 0)],
                )


class TestNull(TestCase):

    def test_all(self):
        NULL = Null
        self.assertTrue(NULL + 1 is Null)
        self.assertTrue(1 + NULL is Null)
        NULL += 4
        self.assertTrue(NULL is Null)
        value = 5
        value += NULL
        self.assertTrue(value is Null)

        self.assertTrue(NULL - 2 is Null)
        self.assertTrue(2 - NULL is Null)
        NULL -= 5
        self.assertTrue(NULL is Null)
        value = 6
        value -= NULL
        self.assertTrue(value is Null)

        self.assertTrue(NULL / 0 is Null)
        self.assertTrue(3 / NULL is Null)
        NULL /= 6
        self.assertTrue(NULL is Null)
        value = 7
        value /= NULL
        self.assertTrue(value is Null)

        self.assertTrue(NULL * -3 is Null)
        self.assertTrue(4 * NULL is Null)
        NULL *= 7
        self.assertTrue(NULL is Null)
        value = 8
        value *= NULL
        self.assertTrue(value is Null)

        self.assertTrue(NULL % 1 is Null)
        self.assertTrue(7 % NULL is Null)
        NULL %= 1
        self.assertTrue(NULL is Null)
        value = 9
        value %= NULL
        self.assertTrue(value is Null)

        self.assertTrue(NULL ** 2 is Null)
        self.assertTrue(4 ** NULL is Null)
        NULL **= 3
        self.assertTrue(NULL is Null)
        value = 9
        value **= NULL
        self.assertTrue(value is Null)

        self.assertTrue(NULL & 1 is Null)
        self.assertTrue(1 & NULL is Null)
        NULL &= 1
        self.assertTrue(NULL is Null)
        value = 1
        value &= NULL
        self.assertTrue(value is Null)

        self.assertTrue(NULL ^ 1 is Null)
        self.assertTrue(1 ^ NULL is Null)
        NULL ^= 1
        self.assertTrue(NULL is Null)
        value = 1
        value ^= NULL
        self.assertTrue(value is Null)

        self.assertTrue(NULL | 1 is Null)
        self.assertTrue(1 | NULL is Null)
        NULL |= 1
        self.assertTrue(NULL is Null)
        value = 1
        value |= NULL
        self.assertTrue(value is Null)

        self.assertTrue(str(divmod(NULL, 1)) == '(<null>, <null>)')
        self.assertTrue(str(divmod(1, NULL)) == '(<null>, <null>)')

        self.assertTrue(NULL << 1 is Null)
        self.assertTrue(2 << NULL is Null)
        NULL <<=3
        self.assertTrue(NULL is Null)
        value = 9
        value <<= NULL
        self.assertTrue(value is Null)

        self.assertTrue(NULL >> 1 is Null)
        self.assertTrue(2 >> NULL is Null)
        NULL >>= 3
        self.assertTrue(NULL is Null)
        value = 9
        value >>= NULL
        self.assertTrue(value is Null)

        self.assertTrue(-NULL is Null)
        self.assertTrue(+NULL is Null)
        self.assertTrue(abs(NULL) is Null)
        self.assertTrue(~NULL is Null)

        self.assertTrue(NULL.attr is Null)
        self.assertTrue(NULL() is Null)
        self.assertTrue(getattr(NULL, 'fake') is Null)

        self.assertRaises(TypeError, hash, NULL)

class TestLogical(TestCase):
    "Testing Logical"

    def test_unknown(self):
        for unk in '', '?', ' ', None, Null, Unknown:
            huh = Logical(unk)
            self.assertEqual(huh == None, True, "huh is %r from %r, which is not None" % (huh, unk))
            self.assertEqual(huh != None, False, "huh is %r from %r, which is not None" % (huh, unk))
            self.assertEqual(huh != True, True, "huh is %r from %r, which is not None" % (huh, unk))
            self.assertEqual(huh == True, False, "huh is %r from %r, which is not None" % (huh, unk))
            self.assertEqual(huh != False, True, "huh is %r from %r, which is not None" % (huh, unk))
            self.assertEqual(huh == False, False, "huh is %r from %r, which is not None" % (huh, unk))
            self.assertRaises(ValueError, lambda : (0, 1, 2)[huh])

    def test_true(self):
        for true in 'True', 'yes', 't', 'Y', 7, ['blah']:
            huh = Logical(true)
            self.assertEqual(huh == True, True)
            self.assertEqual(huh != True, False)
            self.assertEqual(huh == False, False, "%r is not True" % true)
            self.assertEqual(huh != False, True)
            self.assertEqual(huh == None, False)
            self.assertEqual(huh != None, True)
            self.assertEqual((0, 1, 2)[huh], 1)

    def test_false(self):
        for false in 'false', 'No', 'F', 'n', 0, []:
            huh = Logical(false)
            self.assertEqual(huh != False, False)
            self.assertEqual(huh == False, True)
            self.assertEqual(huh != True, True)
            self.assertEqual(huh == True, False)
            self.assertEqual(huh != None, True)
            self.assertEqual(huh == None, False)
            self.assertEqual((0, 1, 2)[huh], 0)

    def test_singletons(self):
        heh = Logical(True)
        hah = Logical('Yes')
        ick = Logical(False)
        ack = Logical([])
        unk = Logical('?')
        bla = Logical(None)
        self.assertEqual(heh is hah, True)
        self.assertEqual(ick is ack, True)
        self.assertEqual(unk is bla, True)

    def test_error(self):
        self.assertRaises(ValueError, Logical, 'wrong')

    def test_and(self):
        true = Logical(True)
        false = Logical(False)
        unknown = Logical(None)
        self.assertEqual((true & true) is true, True)
        self.assertEqual((true & false) is false, True)
        self.assertEqual((false & true) is false, True)
        self.assertEqual((false & false) is false, True)
        self.assertEqual((true & unknown) is unknown, True)
        self.assertEqual((false & unknown) is false, True)
        self.assertEqual((unknown & true) is unknown, True)
        self.assertEqual((unknown & false) is false, True)
        self.assertEqual((unknown & unknown) is unknown, True)
        self.assertEqual((true & True) is true, True)
        self.assertEqual((true & False) is false, True)
        self.assertEqual((false & True) is false, True)
        self.assertEqual((false & False) is false, True)
        self.assertEqual((true & None) is unknown, True)
        self.assertEqual((false & None) is false, True)
        self.assertEqual((unknown & True) is unknown, True)
        self.assertEqual((unknown & False) is false, True)
        self.assertEqual((unknown & None) is unknown, True)
        self.assertEqual((True & true) is true, True)
        self.assertEqual((True & false) is false, True)
        self.assertEqual((False & true) is false, True)
        self.assertEqual((False & false) is false, True)
        self.assertEqual((True & unknown) is unknown, True)
        self.assertEqual((False & unknown) is false, True)
        self.assertEqual((None & true) is unknown, True)
        self.assertEqual((None & false) is false, True)
        self.assertEqual((None & unknown) is unknown, True)
        self.assertEqual(type(true & 0), int)
        self.assertEqual(true & 0, 0)
        self.assertEqual(type(true & 3), int)
        self.assertEqual(true & 3, 1)
        self.assertEqual(type(false & 0), int)
        self.assertEqual(false & 0, 0)
        self.assertEqual(type(false & 2), int)
        self.assertEqual(false & 2, 0)
        self.assertEqual(type(unknown & 0), int)
        self.assertEqual(unknown & 0, 0)
        self.assertEqual(unknown & 2, unknown)

        t = true
        t &= true
        self.assertEqual(t is true, True)
        t = true
        t &= false
        self.assertEqual(t is false, True)
        f = false
        f &= true
        self.assertEqual(f is false, True)
        f = false
        f &= false
        self.assertEqual(f is false, True)
        t = true
        t &= unknown
        self.assertEqual(t is unknown, True)
        f = false
        f &= unknown
        self.assertEqual(f is false, True)
        u = unknown
        u &= true
        self.assertEqual(u is unknown, True)
        u = unknown
        u &= false
        self.assertEqual(u is false, True)
        u = unknown
        u &= unknown
        self.assertEqual(u is unknown, True)
        t = true
        t &= True
        self.assertEqual(t is true, True)
        t = true
        t &= False
        self.assertEqual(t is false, True)
        f = false
        f &= True
        self.assertEqual(f is false, True)
        f = false
        f &= False
        self.assertEqual(f is false, True)
        t = true
        t &= None
        self.assertEqual(t is unknown, True)
        f = false
        f &= None
        self.assertEqual(f is false, True)
        u = unknown
        u &= True
        self.assertEqual(u is unknown, True)
        u = unknown
        u &= False
        self.assertEqual(u is false, True)
        u = unknown
        u &= None
        self.assertEqual(u is unknown, True)
        t = True
        t &= true
        self.assertEqual(t is true, True)
        t = True
        t &= false
        self.assertEqual(t is false, True)
        f = False
        f &= true
        self.assertEqual(f is false, True)
        f = False
        f &= false
        self.assertEqual(f is false, True)
        t = True
        t &= unknown
        self.assertEqual(t is unknown, True)
        f = False
        f &= unknown
        self.assertEqual(f is false, True)
        u = None
        u &= true
        self.assertEqual(u is unknown, True)
        u = None
        u &= false
        self.assertEqual(u is false, True)
        u = None
        u &= unknown
        self.assertEqual(u is unknown, True)
        t = true
        t &= 0
        self.assertEqual(type(true & 0), int)
        t = true
        t &= 0
        self.assertEqual(true & 0, 0)
        t = true
        t &= 3
        self.assertEqual(type(true & 3), int)
        t = true
        t &= 3
        self.assertEqual(true & 3, 1)
        f = false
        f &= 0
        self.assertEqual(type(false & 0), int)
        f = false
        f &= 0
        self.assertEqual(false & 0, 0)
        f = false
        f &= 2
        self.assertEqual(type(false & 2), int)
        f = false
        f &= 2
        self.assertEqual(false & 2, 0)
        u = unknown
        u &= 0
        self.assertEqual(type(unknown & 0), int)
        u = unknown
        u &= 0
        self.assertEqual(unknown & 0, 0)
        u = unknown
        u &= 2
        self.assertEqual(unknown & 2, unknown)

    def test_or(self):
        true = Logical(True)
        false = Logical(False)
        unknown = Logical(None)
        self.assertEqual((true | true) is true, True)
        self.assertEqual((true | false) is true, True)
        self.assertEqual((false | true) is true, True)
        self.assertEqual((false | false) is false, True)
        self.assertEqual((true | unknown) is true, True)
        self.assertEqual((false | unknown) is unknown, True)
        self.assertEqual((unknown | true) is true, True)
        self.assertEqual((unknown | false) is unknown, True)
        self.assertEqual((unknown | unknown) is unknown, True)
        self.assertEqual((true | True) is true, True)
        self.assertEqual((true | False) is true, True)
        self.assertEqual((false | True) is true, True)
        self.assertEqual((false | False) is false, True)
        self.assertEqual((true | None) is true, True)
        self.assertEqual((false | None) is unknown, True)
        self.assertEqual((unknown | True) is true, True)
        self.assertEqual((unknown | False) is unknown, True)
        self.assertEqual((unknown | None) is unknown, True)
        self.assertEqual((True | true) is true, True)
        self.assertEqual((True | false) is true, True)
        self.assertEqual((False | true) is true, True)
        self.assertEqual((False | false) is false, True)
        self.assertEqual((True | unknown) is true, True)
        self.assertEqual((False | unknown) is unknown, True)
        self.assertEqual((None | true) is true, True)
        self.assertEqual((None | false) is unknown, True)
        self.assertEqual((None | unknown) is unknown, True)
        self.assertEqual(type(true | 0), int)
        self.assertEqual(true | 0, 1)
        self.assertEqual(type(true | 2), int)
        self.assertEqual(true | 2, 3)
        self.assertEqual(type(false | 0), int)
        self.assertEqual(false | 0, 0)
        self.assertEqual(type(false | 2), int)
        self.assertEqual(false | 2, 2)
        self.assertEqual(unknown | 0, unknown)
        self.assertEqual(unknown | 2, unknown)

        t = true
        t |= true
        self.assertEqual(t is true, True)
        t = true
        t |= false
        self.assertEqual(t is true, True)
        f = false
        f |= true
        self.assertEqual(f is true, True)
        f = false
        f |= false
        self.assertEqual(f is false, True)
        t = true
        t |= unknown
        self.assertEqual(t is true, True)
        f = false
        f |= unknown
        self.assertEqual(f is unknown, True)
        u = unknown
        u |= true
        self.assertEqual(u is true, True)
        u = unknown
        u |= false
        self.assertEqual(u is unknown, True)
        u = unknown
        u |= unknown
        self.assertEqual(u is unknown, True)
        t = true
        t |= True
        self.assertEqual(t is true, True)
        t = true
        t |= False
        self.assertEqual(t is true, True)
        f = false
        f |= True
        self.assertEqual(f is true, True)
        f = false
        f |= False
        self.assertEqual(f is false, True)
        t = true
        t |= None
        self.assertEqual(t is true, True)
        f = false
        f |= None
        self.assertEqual(f is unknown, True)
        u = unknown
        u |= True
        self.assertEqual(u is true, True)
        u = unknown
        u |= False
        self.assertEqual(u is unknown, True)
        u = unknown
        u |= None
        self.assertEqual(u is unknown, True)
        t = True
        t |= true
        self.assertEqual(t is true, True)
        t = True
        t |= false
        self.assertEqual(t is true, True)
        f = False
        f |= true
        self.assertEqual(f is true, True)
        f = False
        f |= false
        self.assertEqual(f is false, True)
        t = True
        t |= unknown
        self.assertEqual(t is true, True)
        f = False
        f |= unknown
        self.assertEqual(f is unknown, True)
        u = None
        u |= true
        self.assertEqual(u is true, True)
        u = None
        u |= false
        self.assertEqual(u is unknown, True)
        u = None
        u |= unknown
        self.assertEqual(u is unknown, True)
        t = true
        t |= 0
        self.assertEqual(type(t), int)
        t = true
        t |= 0
        self.assertEqual(t, 1)
        t = true
        t |= 2
        self.assertEqual(type(t), int)
        t = true
        t |= 2
        self.assertEqual(t, 3)
        f = false
        f |= 0
        self.assertEqual(type(f), int)
        f = false
        f |= 0
        self.assertEqual(f, 0)
        f = false
        f |= 2
        self.assertEqual(type(f), int)
        f = false
        f |= 2
        self.assertEqual(f, 2)
        u = unknown
        u |= 0
        self.assertEqual(u, unknown)

    def test_xor(self):
        true = Logical(True)
        false = Logical(False)
        unknown = Logical(None)
        self.assertEqual((true ^ true) is false, True)
        self.assertEqual((true ^ false) is true, True)
        self.assertEqual((false ^ true) is true, True)
        self.assertEqual((false ^ false) is false, True)
        self.assertEqual((true ^ unknown) is unknown, True)
        self.assertEqual((false ^ unknown) is unknown, True)
        self.assertEqual((unknown ^ true) is unknown, True)
        self.assertEqual((unknown ^ false) is unknown, True)
        self.assertEqual((unknown ^ unknown) is unknown, True)
        self.assertEqual((true ^ True) is false, True)
        self.assertEqual((true ^ False) is true, True)
        self.assertEqual((false ^ True) is true, True)
        self.assertEqual((false ^ False) is false, True)
        self.assertEqual((true ^ None) is unknown, True)
        self.assertEqual((false ^ None) is unknown, True)
        self.assertEqual((unknown ^ True) is unknown, True)
        self.assertEqual((unknown ^ False) is unknown, True)
        self.assertEqual((unknown ^ None) is unknown, True)
        self.assertEqual((True ^ true) is false, True)
        self.assertEqual((True ^ false) is true, True)
        self.assertEqual((False ^ true) is true, True)
        self.assertEqual((False ^ false) is false, True)
        self.assertEqual((True ^ unknown) is unknown, True)
        self.assertEqual((False ^ unknown) is unknown, True)
        self.assertEqual((None ^ true) is unknown, True)
        self.assertEqual((None ^ false) is unknown, True)
        self.assertEqual((None ^ unknown) is unknown, True)
        self.assertEqual(type(true ^ 2), int)
        self.assertEqual(true ^ 2, 3)
        self.assertEqual(type(true ^ 0), int)
        self.assertEqual(true ^ 0, 1)
        self.assertEqual(type(false ^ 0), int)
        self.assertEqual(false ^ 0, 0)
        self.assertEqual(type(false ^ 2), int)
        self.assertEqual(false ^ 2, 2)
        self.assertEqual(unknown ^ 0, unknown)
        self.assertEqual(unknown ^ 2, unknown)

        t = true
        t ^= true
        self.assertEqual(t is false, True)
        t = true
        t ^= false
        self.assertEqual(t is true, True)
        f = false
        f ^= true
        self.assertEqual(f is true, True)
        f = false
        f ^= false
        self.assertEqual(f is false, True)
        t = true
        t ^= unknown
        self.assertEqual(t is unknown, True)
        f = false
        f ^= unknown
        self.assertEqual(f is unknown, True)
        u = unknown
        u ^= true
        self.assertEqual(u is unknown, True)
        u = unknown
        u ^= false
        self.assertEqual(u is unknown, True)
        u = unknown
        u ^= unknown
        self.assertEqual(u is unknown, True)
        t = true
        t ^= True
        self.assertEqual(t is false, True)
        t = true
        t ^= False
        self.assertEqual(t is true, True)
        f = false
        f ^= True
        self.assertEqual(f is true, True)
        f = false
        f ^= False
        self.assertEqual(f is false, True)
        t = true
        t ^= None
        self.assertEqual(t is unknown, True)
        f = false
        f ^= None
        self.assertEqual(f is unknown, True)
        u = unknown
        u ^= True
        self.assertEqual(u is unknown, True)
        u = unknown
        u ^= False
        self.assertEqual(u is unknown, True)
        u = unknown
        u ^= None
        self.assertEqual(u is unknown, True)
        t = True
        t ^= true
        self.assertEqual(t is false, True)
        t = True
        t ^= false
        self.assertEqual(t is true, True)
        f = False
        f ^= true
        self.assertEqual(f is true, True)
        f = False
        f ^= false
        self.assertEqual(f is false, True)
        t = True
        t ^= unknown
        self.assertEqual(t is unknown, True)
        f = False
        f ^= unknown
        self.assertEqual(f is unknown, True)
        u = None
        u ^= true
        self.assertEqual(u is unknown, True)
        u = None
        u ^= false
        self.assertEqual(u is unknown, True)
        u = None
        u ^= unknown
        self.assertEqual(u is unknown, True)
        t = true
        t ^= 0
        self.assertEqual(type(true ^ 0), int)
        t = true
        t ^= 0
        self.assertEqual(true ^ 0, 1)
        t = true
        t ^= 2
        self.assertEqual(type(true ^ 2), int)
        t = true
        t ^= 2
        self.assertEqual(true ^ 2, 3)
        f = false
        f ^= 0
        self.assertEqual(type(false ^ 0), int)
        f = false
        f ^= 0
        self.assertEqual(false ^ 0, 0)
        f = false
        f ^= 2
        self.assertEqual(type(false ^ 2), int)
        f = false
        f ^= 2
        self.assertEqual(false ^ 2, 2)
        u = unknown
        u ^= 0
        self.assertEqual(unknown ^ 0, unknown)
        u = unknown
        u ^= 2
        self.assertEqual(unknown ^ 2, unknown)

    def test_negation(self):
        true = Logical(True)
        false = Logical(False)
        none = Logical(None)
        self.assertEqual(-true, -1)
        self.assertEqual(-false, 0)
        self.assertEqual(-none, none)

    def test_posation(self):
        true = Logical(True)
        false = Logical(False)
        none = Logical(None)
        self.assertEqual(+true, 1)
        self.assertEqual(+false, 0)
        self.assertEqual(+none, none)

    def test_abs(self):
        true = Logical(True)
        false = Logical(False)
        none = Logical(None)
        self.assertEqual(abs(true), 1)
        self.assertEqual(abs(false), 0)
        self.assertEqual(abs(none), none)

    def test_invert(self):
        true = Logical(True)
        false = Logical(False)
        none = Logical(None)
        self.assertEqual(~true, false)
        self.assertEqual(~false, true)
        self.assertEqual(~none, none)

    def test_complex(self):
        true = Logical(True)
        false = Logical(False)
        none = Logical(None)
        self.assertEqual(complex(true), complex(1))
        self.assertEqual(complex(false), complex(0))
        self.assertRaises(ValueError, complex, none)

    def test_int(self):
        true = Logical(True)
        false = Logical(False)
        none = Logical(None)
        self.assertEqual(int(true), 1)
        self.assertEqual(int(false), 0)
        self.assertRaises(ValueError, int, none)

    if PY_VER < (3, 0):
        def test_long(self):
            true = Logical(True)
            false = Logical(False)
            none = Logical(None)
            self.assertEqual(long(true), long(1))
            self.assertEqual(long(false), long(0))
            self.assertRaises(ValueError, long, none)

    def test_float(self):
        true = Logical(True)
        false = Logical(False)
        none = Logical(None)
        self.assertEqual(float(true), 1.0)
        self.assertEqual(float(false), 0.0)
        self.assertRaises(ValueError, float, none)

    def test_oct(self):
        true = Logical(True)
        false = Logical(False)
        none = Logical(None)
        self.assertEqual(oct(true), oct(1))
        self.assertEqual(oct(false), oct(0))
        self.assertRaises(ValueError, oct, none)

    def test_hex(self):
        true = Logical(True)
        false = Logical(False)
        none = Logical(None)
        self.assertEqual(hex(true), hex(1))
        self.assertEqual(hex(false), hex(0))
        self.assertRaises(ValueError, hex, none)

    def test_addition(self):
        true = Logical(True)
        false = Logical(False)
        unknown = Logical(None)
        self.assertEqual(true + true, 2)
        self.assertEqual(true + false, 1)
        self.assertEqual(false + true, 1)
        self.assertEqual(false + false, 0)
        self.assertEqual(true + unknown, unknown)
        self.assertEqual(false + unknown, unknown)
        self.assertEqual(unknown + true, unknown)
        self.assertEqual(unknown + false, unknown)
        self.assertEqual(unknown + unknown, unknown)
        self.assertEqual(true + True, 2)
        self.assertEqual(true + False, 1)
        self.assertEqual(false + True, 1)
        self.assertEqual(false + False, 0)
        self.assertEqual(true + None, unknown)
        self.assertEqual(false + None, unknown)
        self.assertEqual(unknown + True, unknown)
        self.assertEqual(unknown + False, unknown)
        self.assertEqual(unknown + None, unknown)
        self.assertEqual(True + true, 2)
        self.assertEqual(True + false, 1)
        self.assertEqual(False + true, 1)
        self.assertEqual(False + false, 0)
        self.assertEqual(True + unknown, unknown)
        self.assertEqual(False + unknown, unknown)
        self.assertEqual(None + true, unknown)
        self.assertEqual(None + false, unknown)
        self.assertEqual(None + unknown, unknown)

        t = true
        t += true
        self.assertEqual(t, 2)
        t = true
        t += false
        self.assertEqual(t, 1)
        f = false
        f += true
        self.assertEqual(f, 1)
        f = false
        f += false
        self.assertEqual(f, 0)
        t = true
        t += unknown
        self.assertEqual(t, unknown)
        f = false
        f += unknown
        self.assertEqual(f, unknown)
        u = unknown
        u += true
        self.assertEqual(u, unknown)
        u = unknown
        u += false
        self.assertEqual(u, unknown)
        u = unknown
        u += unknown
        self.assertEqual(u, unknown)
        t = true
        t += True
        self.assertEqual(t, 2)
        t = true
        t += False
        self.assertEqual(t, 1)
        f = false
        f += True
        self.assertEqual(f, 1)
        f = false
        f += False
        self.assertEqual(f, 0)
        t = true
        t += None
        self.assertEqual(t, unknown)
        f = false
        f += None
        self.assertEqual(f, unknown)
        u = unknown
        u += True
        self.assertEqual(u, unknown)
        u = unknown
        u += False
        self.assertEqual(u, unknown)
        u = unknown
        u += None
        self.assertEqual(u, unknown)
        t = True
        t += true
        self.assertEqual(t, 2)
        t = True
        t += false
        self.assertEqual(t, 1)
        f = False
        f += true
        self.assertEqual(f, 1)
        f = False
        f += false
        self.assertEqual(f, 0)
        t = True
        t += unknown
        self.assertEqual(t, unknown)
        f = False
        f += unknown
        self.assertEqual(f, unknown)
        u = None
        u += true
        self.assertEqual(u, unknown)
        u = None
        u += false
        self.assertEqual(u, unknown)
        u = None
        u += unknown
        self.assertEqual(u, unknown)

    def test_multiplication(self):
        true = Logical(True)
        false = Logical(False)
        unknown = Logical(None)
        self.assertEqual(true * true, 1)
        self.assertEqual(true * false, 0)
        self.assertEqual(false * true, 0)
        self.assertEqual(false * false, 0)
        self.assertEqual(true * unknown, unknown)
        self.assertEqual(false * unknown, 0)
        self.assertEqual(unknown * true, unknown)
        self.assertEqual(unknown * false, 0)
        self.assertEqual(unknown * unknown, unknown)
        self.assertEqual(true * True, 1)
        self.assertEqual(true * False, 0)
        self.assertEqual(false * True, 0)
        self.assertEqual(false * False, 0)
        self.assertEqual(true * None, unknown)
        self.assertEqual(false * None, 0)
        self.assertEqual(unknown * True, unknown)
        self.assertEqual(unknown * False, 0)
        self.assertEqual(unknown * None, unknown)
        self.assertEqual(True * true, 1)
        self.assertEqual(True * false, 0)
        self.assertEqual(False * true, 0)
        self.assertEqual(False * false, 0)
        self.assertEqual(True * unknown, unknown)
        self.assertEqual(False * unknown, 0)
        self.assertEqual(None * true, unknown)
        self.assertEqual(None * false, 0)
        self.assertEqual(None * unknown, unknown)

        t = true
        t *= true
        self.assertEqual(t, 1)
        t = true
        t *= false
        self.assertEqual(t, 0)
        f = false
        f *= true
        self.assertEqual(f, 0)
        f = false
        f *= false
        self.assertEqual(f, 0)
        t = true
        t *= unknown
        self.assertEqual(t, unknown)
        f = false
        f *= unknown
        self.assertEqual(f, 0)
        u = unknown
        u *= true
        self.assertEqual(u, unknown)
        u = unknown
        u *= false
        self.assertEqual(u, 0)
        u = unknown
        u *= unknown
        self.assertEqual(u, unknown)
        t = true
        t *= True
        self.assertEqual(t, 1)
        t = true
        t *= False
        self.assertEqual(t, 0)
        f = false
        f *= True
        self.assertEqual(f, 0)
        f = false
        f *= False
        self.assertEqual(f, 0)
        t = true
        t *= None
        self.assertEqual(t, unknown)
        f = false
        f *= None
        self.assertEqual(f, 0)
        u = unknown
        u *= True
        self.assertEqual(u, unknown)
        u = unknown
        u *= False
        self.assertEqual(u, 0)
        u = unknown
        u *= None
        self.assertEqual(u, unknown)
        t = True
        t *= true
        self.assertEqual(t, 1)
        t = True
        t *= false
        self.assertEqual(t, 0)
        f = False
        f *= true
        self.assertEqual(f, 0)
        f = False
        f *= false
        self.assertEqual(f, 0)
        t = True
        t *= unknown
        self.assertEqual(t, unknown)
        f = False
        f *= unknown
        self.assertEqual(f, 0)
        u = None
        u *= true
        self.assertEqual(u, unknown)
        u = None
        u *= false
        self.assertEqual(u, 0)
        u = None
        u *= unknown
        self.assertEqual(u, unknown)

    def test_subtraction(self):
        true = Logical(True)
        false = Logical(False)
        unknown = Logical(None)
        self.assertEqual(true - true, 0)
        self.assertEqual(true - false, 1)
        self.assertEqual(false - true, -1)
        self.assertEqual(false - false, 0)
        self.assertEqual(true - unknown, unknown)
        self.assertEqual(false - unknown, unknown)
        self.assertEqual(unknown - true, unknown)
        self.assertEqual(unknown - false, unknown)
        self.assertEqual(unknown - unknown, unknown)
        self.assertEqual(true - True, 0)
        self.assertEqual(true - False, 1)
        self.assertEqual(false - True, -1)
        self.assertEqual(false - False, 0)
        self.assertEqual(true - None, unknown)
        self.assertEqual(false - None, unknown)
        self.assertEqual(unknown - True, unknown)
        self.assertEqual(unknown - False, unknown)
        self.assertEqual(unknown - None, unknown)
        self.assertEqual(True - true, 0)
        self.assertEqual(True - false, 1)
        self.assertEqual(False - true, -1)
        self.assertEqual(False - false, 0)
        self.assertEqual(True - unknown, unknown)
        self.assertEqual(False - unknown, unknown)
        self.assertEqual(None - true, unknown)
        self.assertEqual(None - false, unknown)
        self.assertEqual(None - unknown, unknown)

        t = true
        t -= true
        self.assertEqual(t, 0)
        t = true
        t -= false
        self.assertEqual(t, 1)
        f = false
        f -= true
        self.assertEqual(f, -1)
        f = false
        f -= false
        self.assertEqual(f, 0)
        t = true
        t -= unknown
        self.assertEqual(t, unknown)
        f = false
        f -= unknown
        self.assertEqual(f, unknown)
        u = unknown
        u -= true
        self.assertEqual(u, unknown)
        u = unknown
        u -= false
        self.assertEqual(u, unknown)
        u = unknown
        u -= unknown
        self.assertEqual(u, unknown)
        t = true
        t -= True
        self.assertEqual(t, 0)
        t = true
        t -= False
        self.assertEqual(t, 1)
        f = false
        f -= True
        self.assertEqual(f, -1)
        f = false
        f -= False
        self.assertEqual(f, 0)
        t = true
        t -= None
        self.assertEqual(t, unknown)
        f = false
        f -= None
        self.assertEqual(f, unknown)
        u = unknown
        u -= True
        self.assertEqual(u, unknown)
        u = unknown
        u -= False
        self.assertEqual(u, unknown)
        u = unknown
        u -= None
        self.assertEqual(u, unknown)
        t = True
        t -= true
        self.assertEqual(t, 0)
        t = True
        t -= false
        self.assertEqual(t, 1)
        f = False
        f -= true
        self.assertEqual(f, -1)
        f = False
        f -= false
        self.assertEqual(f, 0)
        t = True
        t -= unknown
        self.assertEqual(t, unknown)
        f = False
        f -= unknown
        self.assertEqual(f, unknown)
        u = None
        u -= true
        self.assertEqual(u, unknown)
        u = None
        u -= false
        self.assertEqual(u, unknown)
        u = None
        u -= unknown
        self.assertEqual(u, unknown)

    def test_division(self):
        true = Logical(True)
        false = Logical(False)
        unknown = Logical(None)
        self.assertEqual(true / true, 1)
        self.assertEqual(true / false, unknown)
        self.assertEqual(false / true, 0)
        self.assertEqual(false / false, unknown)
        self.assertEqual(true / unknown, unknown)
        self.assertEqual(false / unknown, unknown)
        self.assertEqual(unknown / true, unknown)
        self.assertEqual(unknown / false, unknown)
        self.assertEqual(unknown / unknown, unknown)
        self.assertEqual(true / True, 1)
        self.assertEqual(true / False, unknown)
        self.assertEqual(false / True, 0)
        self.assertEqual(false / False, unknown)
        self.assertEqual(true / None, unknown)
        self.assertEqual(false / None, unknown)
        self.assertEqual(unknown / True, unknown)
        self.assertEqual(unknown / False, unknown)
        self.assertEqual(unknown / None, unknown)
        self.assertEqual(True / true, 1)
        self.assertEqual(True / false, unknown)
        self.assertEqual(False / true, 0)
        self.assertEqual(False / false, unknown)
        self.assertEqual(True / unknown, unknown)
        self.assertEqual(False / unknown, unknown)
        self.assertEqual(None / true, unknown)
        self.assertEqual(None / false, unknown)
        self.assertEqual(None / unknown, unknown)

        t = true
        t /= true
        self.assertEqual(t, 1)
        t = true
        t /= false
        self.assertEqual(t, unknown)
        f = false
        f /= true
        self.assertEqual(f, 0)
        f = false
        f /= false
        self.assertEqual(f, unknown)
        t = true
        t /= unknown
        self.assertEqual(t, unknown)
        f = false
        f /= unknown
        self.assertEqual(f, unknown)
        u = unknown
        u /= true
        self.assertEqual(u, unknown)
        u = unknown
        u /= false
        self.assertEqual(u, unknown)
        u = unknown
        u /= unknown
        self.assertEqual(u, unknown)
        t = true
        t /= True
        self.assertEqual(t, 1)
        t = true
        t /= False
        self.assertEqual(t, unknown)
        f = false
        f /= True
        self.assertEqual(f, 0)
        f = false
        f /= False
        self.assertEqual(f, unknown)
        t = true
        t /= None
        self.assertEqual(t, unknown)
        f = false
        f /= None
        self.assertEqual(f, unknown)
        u = unknown
        u /= True
        self.assertEqual(u, unknown)
        u = unknown
        u /= False
        self.assertEqual(u, unknown)
        u = unknown
        u /= None
        self.assertEqual(u, unknown)
        t = True
        t /= true
        self.assertEqual(t, 1)
        t = True
        t /= false
        self.assertEqual(t, unknown)
        f = False
        f /= true
        self.assertEqual(f, 0)
        f = False
        f /= false
        self.assertEqual(f, unknown)
        t = True
        t /= unknown
        self.assertEqual(t, unknown)
        f = False
        f /= unknown
        self.assertEqual(f, unknown)
        u = None
        u /= true
        self.assertEqual(u, unknown)
        u = None
        u /= false
        self.assertEqual(u, unknown)
        u = None
        u /= unknown
        self.assertEqual(u, unknown)


        self.assertEqual(true // true, 1)
        self.assertEqual(true // false, unknown)
        self.assertEqual(false // true, 0)
        self.assertEqual(false // false, unknown)
        self.assertEqual(true // unknown, unknown)
        self.assertEqual(false // unknown, unknown)
        self.assertEqual(unknown // true, unknown)
        self.assertEqual(unknown // false, unknown)
        self.assertEqual(unknown // unknown, unknown)
        self.assertEqual(true // True, 1)
        self.assertEqual(true // False, unknown)
        self.assertEqual(false // True, 0)
        self.assertEqual(false // False, unknown)
        self.assertEqual(true // None, unknown)
        self.assertEqual(false // None, unknown)
        self.assertEqual(unknown // True, unknown)
        self.assertEqual(unknown // False, unknown)
        self.assertEqual(unknown // None, unknown)
        self.assertEqual(True // true, 1)
        self.assertEqual(True // false, unknown)
        self.assertEqual(False // true, 0)
        self.assertEqual(False // false, unknown)
        self.assertEqual(True // unknown, unknown)
        self.assertEqual(False // unknown, unknown)
        self.assertEqual(None // true, unknown)
        self.assertEqual(None // false, unknown)
        self.assertEqual(None // unknown, unknown)

        t = true
        t //= true
        self.assertEqual(t, 1)
        t = true
        t //= false
        self.assertEqual(t, unknown)
        f = false
        f //= true
        self.assertEqual(f, 0)
        f = false
        f //= false
        self.assertEqual(f, unknown)
        t = true
        t //= unknown
        self.assertEqual(t, unknown)
        f = false
        f //= unknown
        self.assertEqual(f, unknown)
        u = unknown
        u //= true
        self.assertEqual(u, unknown)
        u = unknown
        u //= false
        self.assertEqual(u, unknown)
        u = unknown
        u //= unknown
        self.assertEqual(u, unknown)
        t = true
        t //= True
        self.assertEqual(t, 1)
        t = true
        t //= False
        self.assertEqual(t, unknown)
        f = false
        f //= True
        self.assertEqual(f, 0)
        f = false
        f //= False
        self.assertEqual(f, unknown)
        t = true
        t //= None
        self.assertEqual(t, unknown)
        f = false
        f //= None
        self.assertEqual(f, unknown)
        u = unknown
        u //= True
        self.assertEqual(u, unknown)
        u = unknown
        u //= False
        self.assertEqual(u, unknown)
        u = unknown
        u //= None
        self.assertEqual(u, unknown)
        t = True
        t //= true
        self.assertEqual(t, 1)
        t = True
        t //= false
        self.assertEqual(t, unknown)
        f = False
        f //= true
        self.assertEqual(f, 0)
        f = False
        f //= false
        self.assertEqual(f, unknown)
        t = True
        t //= unknown
        self.assertEqual(t, unknown)
        f = False
        f //= unknown
        self.assertEqual(f, unknown)
        u = None
        u //= true
        self.assertEqual(u, unknown)
        u = None
        u //= false
        self.assertEqual(u, unknown)
        u = None
        u //= unknown
        self.assertEqual(u, unknown)

    def test_shift(self):
        true = Logical(True)
        false = Logical(False)
        unknown = Logical(None)

        self.assertEqual(true >> true, 0)
        self.assertEqual(true >> false, 1)
        self.assertEqual(false >> true, 0)
        self.assertEqual(false >> false, 0)
        self.assertEqual(true >> unknown, unknown)
        self.assertEqual(false >> unknown, unknown)
        self.assertEqual(unknown >> true, unknown)
        self.assertEqual(unknown >> false, unknown)
        self.assertEqual(unknown >> unknown, unknown)
        self.assertEqual(true >> True, 0)
        self.assertEqual(true >> False, 1)
        self.assertEqual(false >> True, 0)
        self.assertEqual(false >> False, 0)
        self.assertEqual(true >> None, unknown)
        self.assertEqual(false >> None, unknown)
        self.assertEqual(unknown >> True, unknown)
        self.assertEqual(unknown >> False, unknown)
        self.assertEqual(unknown >> None, unknown)
        self.assertEqual(True >> true, 0)
        self.assertEqual(True >> false, 1)
        self.assertEqual(False >> true, 0)
        self.assertEqual(False >> false, 0)
        self.assertEqual(True >> unknown, unknown)
        self.assertEqual(False >> unknown, unknown)
        self.assertEqual(None >> true, unknown)
        self.assertEqual(None >> false, unknown)
        self.assertEqual(None >> unknown, unknown)

        self.assertEqual(true << true, 2)
        self.assertEqual(true << false, 1)
        self.assertEqual(false << true, 0)
        self.assertEqual(false << false, 0)
        self.assertEqual(true << unknown, unknown)
        self.assertEqual(false << unknown, unknown)
        self.assertEqual(unknown << true, unknown)
        self.assertEqual(unknown << false, unknown)
        self.assertEqual(unknown << unknown, unknown)
        self.assertEqual(true << True, 2)
        self.assertEqual(true << False, 1)
        self.assertEqual(false << True, 0)
        self.assertEqual(false << False, 0)
        self.assertEqual(true << None, unknown)
        self.assertEqual(false << None, unknown)
        self.assertEqual(unknown << True, unknown)
        self.assertEqual(unknown << False, unknown)
        self.assertEqual(unknown << None, unknown)
        self.assertEqual(True << true, 2)
        self.assertEqual(True << false, 1)
        self.assertEqual(False << true, 0)
        self.assertEqual(False << false, 0)
        self.assertEqual(True << unknown, unknown)
        self.assertEqual(False << unknown, unknown)
        self.assertEqual(None << true, unknown)
        self.assertEqual(None << false, unknown)
        self.assertEqual(None << unknown, unknown)

        t = true
        t >>= true
        self.assertEqual(t, 0)
        t = true
        t >>= false
        self.assertEqual(t, 1)
        f = false
        f >>= true
        self.assertEqual(f, 0)
        f = false
        f >>= false
        self.assertEqual(f, 0)
        t = true
        t >>= unknown
        self.assertEqual(t, unknown)
        f = false
        f >>= unknown
        self.assertEqual(f, unknown)
        u = unknown
        u >>= true
        self.assertEqual(u, unknown)
        u = unknown
        u >>= false
        self.assertEqual(u, unknown)
        u = unknown
        u >>= unknown
        self.assertEqual(u, unknown)
        t = true
        t >>= True
        self.assertEqual(t, 0)
        t = true
        t >>= False
        self.assertEqual(t, 1)
        f = false
        f >>= True
        self.assertEqual(f, 0)
        f = false
        f >>= False
        self.assertEqual(f, 0)
        t = true
        t >>= None
        self.assertEqual(t, unknown)
        f = false
        f >>= None
        self.assertEqual(f, unknown)
        u = unknown
        u >>= True
        self.assertEqual(u, unknown)
        u = unknown
        u >>= False
        self.assertEqual(u, unknown)
        u = unknown
        u >>= None
        self.assertEqual(u, unknown)
        t = True
        t >>= true
        self.assertEqual(t, 0)
        t = True
        t >>= false
        self.assertEqual(t, 1)
        f = False
        f >>= true
        self.assertEqual(f, 0)
        f = False
        f >>= false
        self.assertEqual(f, 0)
        t = True
        t >>= unknown
        self.assertEqual(t, unknown)
        f = False
        f >>= unknown
        self.assertEqual(f, unknown)
        u = None
        u >>= true
        self.assertEqual(u, unknown)
        u = None
        u >>= false
        self.assertEqual(u, unknown)
        u = None
        u >>= unknown
        self.assertEqual(u, unknown)

        t = true
        t <<= true
        self.assertEqual(t, 2)
        t = true
        t <<= false
        self.assertEqual(t, 1)
        f = false
        f <<= true
        self.assertEqual(f, 0)
        f = false
        f <<= false
        self.assertEqual(f, 0)
        t = true
        t <<= unknown
        self.assertEqual(t, unknown)
        f = false
        f <<= unknown
        self.assertEqual(f, unknown)
        u = unknown
        u <<= true
        self.assertEqual(u, unknown)
        u = unknown
        u <<= false
        self.assertEqual(u, unknown)
        u = unknown
        u <<= unknown
        self.assertEqual(u, unknown)
        t = true
        t <<= True
        self.assertEqual(t, 2)
        t = true
        t <<= False
        self.assertEqual(t, 1)
        f = false
        f <<= True
        self.assertEqual(f, 0)
        f = false
        f <<= False
        self.assertEqual(f, 0)
        t = true
        t <<= None
        self.assertEqual(t, unknown)
        f = false
        f <<= None
        self.assertEqual(f, unknown)
        u = unknown
        u <<= True
        self.assertEqual(u, unknown)
        u = unknown
        u <<= False
        self.assertEqual(u, unknown)
        u = unknown
        u <<= None
        self.assertEqual(u, unknown)
        t = True
        t <<= true
        self.assertEqual(t, 2)
        t = True
        t <<= false
        self.assertEqual(t, 1)
        f = False
        f <<= true
        self.assertEqual(f, 0)
        f = False
        f <<= false
        self.assertEqual(f, 0)
        t = True
        t <<= unknown
        self.assertEqual(t, unknown)
        f = False
        f <<= unknown
        self.assertEqual(f, unknown)
        u = None
        u <<= true
        self.assertEqual(u, unknown)
        u = None
        u <<= false
        self.assertEqual(u, unknown)
        u = None
        u <<= unknown
        self.assertEqual(u, unknown)

    def test_pow(self):
        true = Logical(True)
        false = Logical(False)
        unknown = Logical(None)

        self.assertEqual(true ** true, 1)
        self.assertEqual(true ** false, 1)
        self.assertEqual(false ** true, 0)
        self.assertEqual(false ** false, 1)
        self.assertEqual(true ** unknown, unknown)
        self.assertEqual(false ** unknown, unknown)
        self.assertEqual(unknown ** true, unknown)
        self.assertEqual(unknown ** false, 1)
        self.assertEqual(unknown ** unknown, unknown)
        self.assertEqual(true ** True, 1)
        self.assertEqual(true ** False, 1)
        self.assertEqual(false ** True, 0)
        self.assertEqual(false ** False, 1)
        self.assertEqual(true ** None, unknown)
        self.assertEqual(false ** None, unknown)
        self.assertEqual(unknown ** True, unknown)
        self.assertEqual(unknown ** False, 1)
        self.assertEqual(unknown ** None, unknown)
        self.assertEqual(True ** true, 1)
        self.assertEqual(True ** false, 1)
        self.assertEqual(False ** true, 0)
        self.assertEqual(False ** false, 1)
        self.assertEqual(True ** unknown, unknown)
        self.assertEqual(False ** unknown, unknown)
        self.assertEqual(None ** true, unknown)
        self.assertEqual(None ** false, 1)
        self.assertEqual(None ** unknown, unknown)

        t = true
        t **= true
        self.assertEqual(t, 1)
        t = true
        t **= false
        self.assertEqual(t, 1)
        f = false
        f **= true
        self.assertEqual(f, 0)
        f = false
        f **= false
        self.assertEqual(f, 1)
        t = true
        t **= unknown
        self.assertEqual(t, unknown)
        f = false
        f **= unknown
        self.assertEqual(f, unknown)
        u = unknown
        u **= true
        self.assertEqual(u, unknown)
        u = unknown
        u **= false
        self.assertEqual(u, 1)
        u = unknown
        u **= unknown
        self.assertEqual(u, unknown)
        t = true
        t **= True
        self.assertEqual(t, 1)
        t = true
        t **= False
        self.assertEqual(t, 1)
        f = false
        f **= True
        self.assertEqual(f, 0)
        f = false
        f **= False
        self.assertEqual(f, 1)
        t = true
        t **= None
        self.assertEqual(t, unknown)
        f = false
        f **= None
        self.assertEqual(f, unknown)
        u = unknown
        u **= True
        self.assertEqual(u, unknown)
        u = unknown
        u **= False
        self.assertEqual(u, 1)
        u = unknown
        u **= None
        self.assertEqual(u, unknown)
        t = True
        t **= true
        self.assertEqual(t, 1)
        t = True
        t **= false
        self.assertEqual(t, 1)
        f = False
        f **= true
        self.assertEqual(f, 0)
        f = False
        f **= false
        self.assertEqual(f, 1)
        t = True
        t **= unknown
        self.assertEqual(t, unknown)
        f = False
        f **= unknown
        self.assertEqual(f, unknown)
        u = None
        u **= true
        self.assertEqual(u, unknown)
        u = None
        u **= false
        self.assertEqual(u, 1)
        u = None
        u **= unknown
        self.assertEqual(u, unknown)

    def test_mod(self):
        true = Logical(True)
        false = Logical(False)
        unknown = Logical(None)

        self.assertEqual(true % true, 0)
        self.assertEqual(true % false, unknown)
        self.assertEqual(false % true, 0)
        self.assertEqual(false % false, unknown)
        self.assertEqual(true % unknown, unknown)
        self.assertEqual(false % unknown, unknown)
        self.assertEqual(unknown % true, unknown)
        self.assertEqual(unknown % false, unknown)
        self.assertEqual(unknown % unknown, unknown)
        self.assertEqual(true % True, 0)
        self.assertEqual(true % False, unknown)
        self.assertEqual(false % True, 0)
        self.assertEqual(false % False, unknown)
        self.assertEqual(true % None, unknown)
        self.assertEqual(false % None, unknown)
        self.assertEqual(unknown % True, unknown)
        self.assertEqual(unknown % False, unknown)
        self.assertEqual(unknown % None, unknown)
        self.assertEqual(True % true, 0)
        self.assertEqual(True % false, unknown)
        self.assertEqual(False % true, 0)
        self.assertEqual(False % false, unknown)
        self.assertEqual(True % unknown, unknown)
        self.assertEqual(False % unknown, unknown)
        self.assertEqual(None % true, unknown)
        self.assertEqual(None % false, unknown)
        self.assertEqual(None % unknown, unknown)

        t = true
        t %= true
        self.assertEqual(t, 0)
        t = true
        t %= false
        self.assertEqual(t, unknown)
        f = false
        f %= true
        self.assertEqual(f, 0)
        f = false
        f %= false
        self.assertEqual(f, unknown)
        t = true
        t %= unknown
        self.assertEqual(t, unknown)
        f = false
        f %= unknown
        self.assertEqual(f, unknown)
        u = unknown
        u %= true
        self.assertEqual(u, unknown)
        u = unknown
        u %= false
        self.assertEqual(u, unknown)
        u = unknown
        u %= unknown
        self.assertEqual(u, unknown)
        t = true
        t %= True
        self.assertEqual(t, 0)
        t = true
        t %= False
        self.assertEqual(t, unknown)
        f = false
        f %= True
        self.assertEqual(f, 0)
        f = false
        f %= False
        self.assertEqual(f, unknown)
        t = true
        t %= None
        self.assertEqual(t, unknown)
        f = false
        f %= None
        self.assertEqual(f, unknown)
        u = unknown
        u %= True
        self.assertEqual(u, unknown)
        u = unknown
        u %= False
        self.assertEqual(u, unknown)
        u = unknown
        u %= None
        self.assertEqual(u, unknown)
        t = True
        t %= true
        self.assertEqual(t, 0)
        t = True
        t %= false
        self.assertEqual(t, unknown)
        f = False
        f %= true
        self.assertEqual(f, 0)
        f = False
        f %= false
        self.assertEqual(f, unknown)
        t = True
        t %= unknown
        self.assertEqual(t, unknown)
        f = False
        f %= unknown
        self.assertEqual(f, unknown)
        u = None
        u %= true
        self.assertEqual(u, unknown)
        u = None
        u %= false
        self.assertEqual(u, unknown)
        u = None
        u %= unknown
        self.assertEqual(u, unknown)

    def test_divmod(self):
        true = Logical(True)
        false = Logical(False)
        unknown = Logical(None)

        self.assertEqual(divmod(true, true), (1, 0))
        self.assertEqual(divmod(true, false), (unknown, unknown))
        self.assertEqual(divmod(false, true), (0, 0))
        self.assertEqual(divmod(false, false), (unknown, unknown))
        self.assertEqual(divmod(true, unknown), (unknown, unknown))
        self.assertEqual(divmod(false, unknown), (unknown, unknown))
        self.assertEqual(divmod(unknown, true), (unknown, unknown))
        self.assertEqual(divmod(unknown, false), (unknown, unknown))
        self.assertEqual(divmod(unknown, unknown), (unknown, unknown))
        self.assertEqual(divmod(true, True), (1, 0))
        self.assertEqual(divmod(true, False), (unknown, unknown))
        self.assertEqual(divmod(false, True), (0, 0))
        self.assertEqual(divmod(false, False), (unknown, unknown))
        self.assertEqual(divmod(true, None), (unknown, unknown))
        self.assertEqual(divmod(false, None), (unknown, unknown))
        self.assertEqual(divmod(unknown, True), (unknown, unknown))
        self.assertEqual(divmod(unknown, False), (unknown, unknown))
        self.assertEqual(divmod(unknown, None), (unknown, unknown))
        self.assertEqual(divmod(True, true), (1, 0))
        self.assertEqual(divmod(True, false), (unknown, unknown))
        self.assertEqual(divmod(False, true), (0, 0))
        self.assertEqual(divmod(False, false), (unknown, unknown))
        self.assertEqual(divmod(True, unknown), (unknown, unknown))
        self.assertEqual(divmod(False, unknown), (unknown, unknown))
        self.assertEqual(divmod(None, true), (unknown, unknown))
        self.assertEqual(divmod(None, false), (unknown, unknown))
        self.assertEqual(divmod(None, unknown), (unknown, unknown))



if __name__ == '__main__':
    unittest.main()

