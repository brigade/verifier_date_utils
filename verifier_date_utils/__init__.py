from datetime import date, datetime, time as dtime, timedelta

from logging import getLogger
from time import strptime, strftime, gmtime
from calendar import timegm, Calendar, weekday


logger = getLogger(__name__)
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


# Taken from 2.7's stdlib functools.total_ordering
def _total_ordering(cls):
    """Class decorator that fills in missing ordering methods"""
    convert = {
        '__lt__': [('__gt__', lambda self, other: not (self < other or self == other)),
                   ('__le__', lambda self, other: self < other or self == other),
                   ('__ge__', lambda self, other: not self < other)],
        '__le__': [('__ge__', lambda self, other: not self <= other or self == other),
                   ('__lt__', lambda self, other: self <= other and not self == other),
                   ('__gt__', lambda self, other: not self <= other)],
        '__gt__': [('__lt__', lambda self, other: not (self > other or self == other)),
                   ('__ge__', lambda self, other: self > other or self == other),
                   ('__le__', lambda self, other: not self > other)],
        '__ge__': [('__le__', lambda self, other: (not self >= other) or self == other),
                   ('__gt__', lambda self, other: self >= other and not self == other),
                   ('__lt__', lambda self, other: not self >= other)]
    }
    roots = set(dir(cls)) & set(convert)
    if not roots:
        raise ValueError('must define at least one ordering operation: < > <= >=')
    root = max(roots)       # prefer __lt__ to __le__ to __gt__ to __ge__
    for opname, opfunc in convert[root]:
        if opname not in roots:
            opfunc.__name__ = opname
            opfunc.__doc__ = getattr(int, opname).__doc__
            setattr(cls, opname, opfunc)
    return cls


# Converts the facebook date in format "mm/dd/yyyy" to DB format "yyyy-mm-dd".
# @param date A date string to convert.
# @param format The format of the date string.
# @return A date object.
def convert_datestring_format(datestring, format="%m/%d/%Y"):
    if datestring:
        try:
            value = strptime(datestring, format)
            return strftime('%Y-%m-%d', value)
        except ValueError:
            logger.exception('failed to handle DOB string=%s' % datestring)
    return None


def convert_datestring_to_datetime(datestring, format=DATETIME_FORMAT):
    """Converts a datestring to a datetime object"""
    time_struct = strptime(datestring, format)
    return datetime(*time_struct[0:6])


def convert_date_to_datetime(date):
    """Converts a datetime.date to a datetime.datetime object"""
    return datetime.combine(date, dtime()) if date else None


def date_before(date_cmp, years):
    today = datetime.now()
    then = datetime(today.year - years, today.month, today.day)
    return then > date_cmp


def date_after(*args, **kwargs):
    return not date_before(*args, **kwargs)


def find_day_of_week(year, month, day_of_week, offset=0, use_datetime=False):
    """
    Finds the day-of-week inside of a month
    year = an integer 4-digit year
    month = 1-12
    day_of_week = 0:monday, 6:sunday
    offset = week in the month, 0: first week, 1: second week, etc.
    """
    iter = Calendar().itermonthdates(year, month)
    n = 0

    for value in iter:
        if month != value.month:
            continue

        if day_of_week == weekday(value.year, value.month, value.day):
            if n == offset:
                return convert_date_to_datetime(value) if use_datetime else value
            else:
                n += 1

    return None


def is_recent(datetime_to_compare, *args_for_timedelta, **kwargs_for_timedelta):
    """
    Test if the dt is within the last minute or use the args and kwargs to build a timedelta.
    """
    now = datetime.now()

    if not args_for_timedelta:
        args_for_timedelta = []

    if not kwargs_for_timedelta:
        kwargs_for_timedelta = {'minutes': 1}

    return (now - timedelta(*args_for_timedelta, **kwargs_for_timedelta)) < datetime_to_compare


def time_in_millis(my_time=None):
    """
    Fetches the current time in milliseconds from epoch. By default it uses the UTC time, but you can pass in a any time. Must pass in a time tuple.
    """

    if my_time:
        t = my_time
    else:
        t = gmtime()

    return timegm(t)


def years_ago(some_date, years):
    """Return a date some number of calendar years before some given date.

    Leap years make subtracting multiples of 365 troublesome, so we just frob
    the calendar year and then, if the resulting date is on a nonexistent
    February 29, fall back to Feb 28.

    """
    try:
        new_date = date(some_date.year - years, some_date.month, some_date.day)
    except ValueError:
        new_date = date(some_date.year - years, 2, 28)
    return new_date


# ISO functions are from:
# http://stackoverflow.com/questions/304256/whats-the-best-way-to-find-the-inverse-of-datetime-isocalendar
def iso_year_start(iso_year):
    "The gregorian calendar date of the first day of the given ISO year"
    fourth_jan = date(iso_year, 1, 4)
    delta = timedelta(fourth_jan.isoweekday() - 1)
    return fourth_jan - delta


def iso_to_gregorian(iso_year, iso_week, iso_day):
    "Gregorian calendar date for the given ISO year, week and day"
    year_start = iso_year_start(iso_year)
    return year_start + timedelta(days=iso_day - 1, weeks=iso_week - 1)


_marker = object()
@_total_ordering
class NullableDate(object):
    """
    A bucket of year, month, and day ints, any or all of which can be None

    We do not guarantee it represents a valid date. Maybe a subclass will
    someday.
    """
    timetuple = None  # Cause datetime's comparison operators to return
                      # NotImplemented properly. See http://docs.python.org/rel
                      # ease/2.6.5/library/datetime.html#datetime.date.day.

    def __init__(self, date_datetime_or_none=_marker,
                 year=None, month=None, day=None):
        """
        Pass me a single arg that's a date, a datetime, or None. Alternatively,
        pass zero or more of the ``month``, ``day``, and ``year`` kwargs, which
        can be ints or None.
        """
        if date_datetime_or_none is not _marker:
            if isinstance(date_datetime_or_none, (datetime, date)):
                self.year = date_datetime_or_none.year
                self.month = date_datetime_or_none.month
                self.day = date_datetime_or_none.day
            elif date_datetime_or_none is None:
                self.year = self.month = self.day = None
            else:
                raise TypeError("Can't construct a NullableDate out of %s." % (
                    date_datetime_or_none,))
        else:
            self.year = year
            self.month = month
            self.day = day

    def __nonzero__(self):
        """Return whether I have any non-None parts."""
        return not (self.year is None and
                    self.month is None and
                    self.day is None)

    def is_complete(self):
        """Return whether I have a year, month, and day."""
        return not (self.year is None or
                    self.month is None or
                    self.day is None)

    def __unicode__(self):
        return u'%s-%s-%s' % (self.year, self.month, self.day)

    def __str__(self):
        return self.__unicode__().encode('utf-8')

    def _as_date(self):
        """Return me as a date. Raise ValueError if any part of me is None."""
        if not self.is_complete():
            raise ValueError('Comparison of incomplete dates is not yet '
                             'supported.')
        return date(self.year, self.month, self.day)

    def __lt__(self, other):
        """
        Support comparison of fully specified instances of me with datetimes
        and dates.

        Comparison of incomplete types is undefined so far but might be defined
        in the future.
        """
        # TODO: Support comparison with other NullableDates.
        return self._as_date() < other

    def __eq__(self, other):
        return self._as_date() == other


def day_of_year(month, day):
    """
    Return the ordinal of the day, assuming not a leap year.

    For example, January 3 would be 3, while February 3 would be 34.
    """
    try:
        # 2003 is an arbitrary non-leap year.
        return date(2003, month, day).timetuple().tm_yday
    except ValueError:
        if month == 2 and day == 29:
            return 60
        else:
            raise
