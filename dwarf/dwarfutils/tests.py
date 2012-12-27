from datetime import datetime, timedelta

from django.test import TestCase
from pytz import timezone

from dwarfutils import dateutils


class DateUtilTest(TestCase):

    CORRECT_DATE = datetime(2012, 12, 27, 7, 51, 21)
    CORRECT_UNIX = 1356594681

    def tearDown(self):
        pass

    def test_datetime_now_utc(self):
        now = dateutils.datetime_now_utc()
        almost_now = datetime.utcnow()

        self.assertEquals(almost_now.year, now.year)
        self.assertEquals(almost_now.month, now.month)
        self.assertEquals(almost_now.day, now.day)
        self.assertEquals(almost_now.hour, now.hour)
        self.assertEquals(almost_now.minute, now.minute)
        self.assertEquals(almost_now.second, now.second)

    def test_datetime_to_unix(self):
        unix_t = dateutils.datetime_to_unix(DateUtilTest.CORRECT_DATE)
        self.assertEquals(DateUtilTest.CORRECT_UNIX, unix_t)

        #Check backwards
        date = dateutils.unix_to_datetime(unix_t)
        self.assertEquals(DateUtilTest.CORRECT_DATE.year, date.year)
        self.assertEquals(DateUtilTest.CORRECT_DATE.month, date.month)
        self.assertEquals(DateUtilTest.CORRECT_DATE.day, date.day)
        self.assertEquals(DateUtilTest.CORRECT_DATE.hour, date.hour)
        self.assertEquals(DateUtilTest.CORRECT_DATE.minute, date.minute)
        self.assertEquals(DateUtilTest.CORRECT_DATE.second, date.second)

    def test_unix_to_datetime(self):
        date = dateutils.unix_to_datetime(DateUtilTest.CORRECT_UNIX)

        self.assertEquals(DateUtilTest.CORRECT_DATE.year, date.year)
        self.assertEquals(DateUtilTest.CORRECT_DATE.month, date.month)
        self.assertEquals(DateUtilTest.CORRECT_DATE.day, date.day)
        self.assertEquals(DateUtilTest.CORRECT_DATE.hour, date.hour)
        self.assertEquals(DateUtilTest.CORRECT_DATE.minute, date.minute)
        self.assertEquals(DateUtilTest.CORRECT_DATE.second, date.second)

        # Check backwards
        unix_t = dateutils.datetime_to_unix(date)
        self.assertEquals(DateUtilTest.CORRECT_UNIX, unix_t)

    def test_datetime_utc_to_zone(self):
        amsterdam = timezone('Europe/Amsterdam')  # GMT+1
        eastern = timezone('US/Eastern')  # EST = GMT-5

        date = dateutils.datetime_now_utc()
        gmtp1_date = dateutils.datetime_utc_to_zone(date, amsterdam)
        est_date = dateutils.datetime_utc_to_zone(date, eastern)

        correct_gmtp1_date = date + timedelta(hours=1)
        correct_est_date = date - timedelta(hours=5)

        self.assertEquals(correct_gmtp1_date.hour, gmtp1_date.hour)
        self.assertEquals(correct_est_date.hour, est_date.hour)
