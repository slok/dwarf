from datetime import datetime, timedelta

from django.test import TestCase
from pytz import timezone

from dwarfutils import dateutils, urlutils, checkutils


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

    def test_unix_now_utc(self):
        unix_now = dateutils.unix_now_utc()
        now = dateutils.unix_to_datetime(unix_now)
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

    # When there are hour changes the test breaks. Comment for now
    #def test_datetime_utc_to_zone(self):
        #amsterdam = timezone('Europe/Amsterdam')  # GMT+1
        #date = dateutils.datetime_now_utc()
        #gmtp1_date = dateutils.datetime_utc_to_zone(date, amsterdam)
        #correct_gmtp1_date = date + timedelta(hours=1)
        #self.assertEquals(correct_gmtp1_date.hour, gmtp1_date.hour)

        #eastern = timezone('US/Eastern')  # EST = GMT-5
        #est_date = dateutils.datetime_utc_to_zone(date, eastern)
        #correct_est_date = date - timedelta(hours=5)
        #self.assertEquals(correct_est_date.hour, est_date.hour)


class URLUtilTest(TestCase):

    def test_title_extraction(self):
        urls = {
            "http://google.com": "Google",
            "https://www.djangoproject.com/": "The Web framework for perfectionists with deadlines | Django",
            "https://gitHub.com/": "GitHub \xc2\xb7 Build software better, together.",
            "https://twitter.com/": "Twitter"
        }
        for url, title in urls.items():
            self.assertEquals(title, urlutils.extract_url_title(url))

    def test_percent_encode_url(self):
        bad_url = "https://www.google.es/#hl=es&gs_r n=5&gs_ri=psy-ab&cp="
        good_url = "https://www.google.es/#hl=es&gs_r%20n=5&gs_ri=psy-ab&cp="
        self.assertEquals(good_url, urlutils.percent_encode_url(bad_url))

    def test_host_url(self):
        urls = {
            "http://google.com": "google.com",
            "https://www.djangoproject.com/": "www.djangoproject.com",
            "https://gitHub.com/": "github.com",
            "https://twitter.com/": "twitter.com",
            "http://docs.python.org/2/library/urlparse.html": "docs.python.org"
        }

        for url, host in urls.items():
            self.assertEquals(host, urlutils.extract_url_host(url))

    def test_remove_http(self):
        urls = {
            "http://google.com": "google.com",
            "http://www.djangoproject.com/": "www.djangoproject.com/",
            "http://github.com/": "github.com/",
            "http://twitter.com/": "twitter.com/",
            "http://docs.python.org/2/library/urlparse.html": "docs.python.org/2/library/urlparse.html"
        }

        for url, good_url in urls.items():
            self.assertEquals(good_url, urlutils.remove_http_prefix(url))

    def test_remove_https(self):
        urls = {
            "https://google.com": "google.com",
            "https://www.djangoproject.com/": "www.djangoproject.com/",
            "https://github.com/": "github.com/",
            "https://twitter.com/": "twitter.com/",
            "https://docs.python.org/2/library/urlparse.html": "docs.python.org/2/library/urlparse.html"
        }

        for url, good_url in urls.items():
            self.assertEquals(good_url, urlutils.remove_https_prefix(url))

    def test_sanitize(self):

        urls = {
            "HTTP://google.com": "http://google.com",
            "https://www.dJangoProjecT.com/": "https://www.djangoproject.com/",
        }

        for url, good_url in urls.items():
            self.assertEquals(good_url, urlutils.sanitize_url(url))


class CheckUtilTest(TestCase):

    def test_correct_username(self):
        usernames = {
            "slok69": True,
            "sharem": True,
            "-wrong": False,
            "right-": True,
            "rig-ht": True,
            "wro_ng": False,
            "wr0ng_": False,
            "r1ght-": True,
            "_wrong": False,
            "w?rong": False,
            "wr@ong": False,
            "wr#ng": False,
            "wrong+": False,
            "wro/g": False,
            "wro ng": False,
        }
        for username, result in usernames.items():
            self.assertEquals(result, checkutils.username_correct(username))
