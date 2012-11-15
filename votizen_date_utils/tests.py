from calendar import timegm
from datetime import datetime, timedelta, date
from time import gmtime
from unittest import TestCase

from mock import patch
from nose.tools import eq_, ok_, raises

***REMOVED***
    convert_datestring_to_datetime, convert_date_to_datetime,
    date_before, date_after, find_day_of_week, is_recent,
    time_in_millis, years_ago, iso_year_start, iso_to_gregorian,
    NullableDate)


class DateParsingTestCase(TestCase):
    def test_convert_datestring_format(self):

        # Some simple date conversions
        eq_(convert_datestring_format('12/31/2020'), '2020-12-31')
        eq_(convert_datestring_format('06/02/1982'), '1982-06-02')
        eq_(convert_datestring_format('01/01/1972'), '1972-01-01')

        # Check a format that isn't the default;
        # fails by default, but succeeds if you provide the format
        eq_(convert_datestring_format('31-12-2020'), None)
        eq_(convert_datestring_format('31-12-2020', format='%d-%m-%Y'), '2020-12-31')

        eq_(convert_datestring_format(None), None)
        eq_(convert_datestring_format(''), None)
        eq_(convert_datestring_format('asdfag'), None)

    def test_convert_datestring_to_datetime(self):
        # Convert a datestring to a datetime, default format
        eq_(convert_datestring_to_datetime('1982-06-02 14:39:48'), datetime(1982, 6, 2, 14, 39, 48))

        # Convert a datestring to a datetime, explicit format
        eq_(convert_datestring_to_datetime('2/6/1982 14:39', format='%d/%m/%Y %H:%M'), datetime(1982, 6, 2, 14, 39, 0))

    def test_convert_date_to_datetime(self):

        # None isn't converted
        eq_(convert_date_to_datetime(None), None)

        # Otherwise, date is converted to a datetime.
        eq_(convert_date_to_datetime(date(1982, 6, 2)), datetime(1982, 6, 2, 0, 0, 0))

    def test_date_before(self):
        next_year = datetime.now() + timedelta(days=400)
        today = datetime.now()
        last_year = datetime.now() - timedelta(days=400)
        back_10_years = datetime.now() - timedelta(days=4000)
        back_20_years = datetime.now() - timedelta(days=8000)

        ok_(not date_before(next_year, years=0))
        ok_(not date_before(next_year, years=1))

        ok_(not date_before(today, years=0))
        ok_(not date_before(today, years=1))

        ok_(date_before(last_year, years=0))
        ok_(date_before(last_year, years=1))
        ok_(not date_before(last_year, years=10))
        ok_(not date_before(last_year, years=20))

        ok_(date_before(back_10_years, years=0))
        ok_(date_before(back_10_years, years=1))
        ok_(date_before(back_10_years, years=10))
        ok_(not date_before(back_10_years, years=20))

        ok_(date_before(back_20_years, years=0))
        ok_(date_before(back_20_years, years=1))
        ok_(date_before(back_20_years, years=10))
        ok_(date_before(back_20_years, years=20))

    def test_date_after(self):
        next_year = datetime.now() + timedelta(days=400)
        today = datetime.now()
        last_year = datetime.now() - timedelta(days=400)
        back_10_years = datetime.now() - timedelta(days=4000)
        back_20_years = datetime.now() - timedelta(days=8000)

        ok_(date_after(next_year, years=0))
        ok_(date_after(next_year, years=1))

        ok_(date_after(today, years=0))
        ok_(date_after(today, years=1))

        ok_(not date_after(last_year, years=0))
        ok_(not date_after(last_year, years=1))
        ok_(date_after(last_year, years=10))
        ok_(date_after(last_year, years=20))

        ok_(not date_after(back_10_years, years=0))
        ok_(not date_after(back_10_years, years=1))
        ok_(not date_after(back_10_years, years=10))
        ok_(date_after(back_10_years, years=20))

        ok_(not date_after(back_20_years, years=0))
        ok_(not date_after(back_20_years, years=1))
        ok_(not date_after(back_20_years, years=10))
        ok_(not date_after(back_20_years, years=20))

    def test_find_day_of_week(self):
        eq_(find_day_of_week(2012, 6, 3), date(2012, 6, 7))
        eq_(find_day_of_week(2012, 6, 3, offset=1), date(2012, 6, 14))
        eq_(find_day_of_week(2012, 6, 3, offset=2), date(2012, 6, 21))
        eq_(find_day_of_week(2012, 6, 3, offset=3), date(2012, 6, 28))
        eq_(find_day_of_week(2012, 6, 3, offset=4), None)

        # A datetime object can be explicitly requested
        eq_(find_day_of_week(2012, 6, 3, use_datetime=True), datetime(2012, 6, 7, 0, 0, 0))

    def test_is_recent(self):
        ok_(is_recent(datetime.now()))
        ok_(not is_recent(datetime.now() - timedelta(minutes=2)))
        ok_(is_recent(datetime.now() - timedelta(minutes=2), minutes=4))

***REMOVED***
    def test_time_in_millis(self, mock_gmtime):
        t = gmtime()
        mock_gmtime.return_value = t
        eq_(timegm(t), time_in_millis())

        t = datetime.now().timetuple()
        eq_(timegm(t), time_in_millis(t))

    def test_years_ago(self):
        eq_(years_ago(date(2012, 4, 25), 4), date(2008, 4, 25))

        # Check Feb 29. Works as-is for leap years, not for others.
        eq_(years_ago(date(2012, 2, 29), 4), date(2008, 2, 29))
        eq_(years_ago(date(2012, 2, 29), 5), date(2007, 2, 28))

    def test_iso_year_start(self):
        eq_(iso_year_start(2012), date(2012, 1, 2))
        eq_(iso_year_start(2011), date(2011, 1, 3))
        eq_(iso_year_start(2010), date(2010, 1, 4))
        eq_(iso_year_start(2009), date(2008, 12, 29))
        eq_(iso_year_start(2008), date(2007, 12, 31))
        eq_(iso_year_start(2007), date(2007, 1, 1))
        eq_(iso_year_start(2006), date(2006, 1, 2))
        eq_(iso_year_start(2005), date(2005, 1, 3))
        eq_(iso_year_start(2004), date(2003, 12, 29))
        eq_(iso_year_start(2003), date(2002, 12, 30))

    def test_iso_to_gregorian(self):
        eq_(iso_to_gregorian(2012, 1, 1), date(2012, 1, 2))
        eq_(iso_to_gregorian(2012, 1, 4), date(2012, 1, 5))
        eq_(iso_to_gregorian(2012, 2, 4), date(2012, 1, 12))
        eq_(iso_to_gregorian(2012, 12, 4), date(2012, 3, 22))


class NullableDateTests(TestCase):
    def test_comparison_complete(self):
        """Make sure comparison of complete dates works."""
        ok_(date(2008, 5, 6) >
                        NullableDate(year=2008, month=5, day=5))
        ok_(date(2008, 5, 6) <
                        NullableDate(year=2008, month=5, day=7))
        ok_(date(2008, 5, 6) ==
                        NullableDate(year=2008, month=5, day=6))
        ok_(NullableDate(year=2008, month=5, day=5) <
                        date(2008, 5, 6))


    @raises(ValueError)
    def test_comparison_incomplete(self):
        """Make sure comparison of incomplete dates raises ValueError."""
        date(2008, 5, 6) > NullableDate(year=2008, month=5)
