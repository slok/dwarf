import random
import calendar
import time

from django.test import TestCase
from django.conf import settings
import redis

from linkshortener import utils
from clickmanager.models import Click


def get_redis_connection():
    return redis.StrictRedis(connection_pool=settings.REDIS_POOL)


class ClickModelTest(TestCase):

    def test_click_basic_object(self):
        token = utils.counter_to_token(random.randrange(0, 100000))
        click_id = random.randrange(0, 100000)
        SO = "linux"
        browser = "firefox"
        ip = "111.222.333.444"
        click_date = calendar.timegm(time.gmtime())
        language = "EN_us"
        location = "US"

        c = Click(click_id, token, ip, SO, browser, click_date, language,
                    location)

        #Check getters
        self.assertEquals(token, c.token)
        self.assertEquals(click_id, c.click_id)
        self.assertEquals(SO, c.so)
        self.assertEquals(browser, c.browser)
        self.assertEquals(ip, c.ip)
        self.assertEquals(click_date, c.click_date)
        self.assertEquals(language, c.language)
        self.assertEquals(location, c.location)

        #Check setters
        c2 = Click()
        c2.token = token
        c2.click_id = click_id
        c2.so = SO
        c2.browser = browser
        c2.ip = ip
        c2.click_date = click_date
        c2.language = language
        c2.location = location

        self.assertEquals(token, c2.token)
        self.assertEquals(click_id, c2.click_id)
        self.assertEquals(SO, c2.so)
        self.assertEquals(browser, c2.browser)
        self.assertEquals(ip, c2.ip)
        self.assertEquals(click_date, c2.click_date)
        self.assertEquals(language, c2.language)
        self.assertEquals(location, c2.location)

    def test_click_basic_object_str(self):
        token = utils.counter_to_token(random.randrange(0, 100000))
        click_id = random.randrange(0, 100000)
        SO = "linux"
        browser = "firefox"
        ip = "111.222.333.444"
        click_date = calendar.timegm(time.gmtime())
        language = "EN_us"
        location = "US"

        c = Click(click_id, token, ip, SO, browser, click_date, language,
                    location)

        format = Click.OBJECT_STR_FORMAT.format(click_id, token, ip, SO,
                                        browser, click_date, language, location)

        self.assertEquals(format, str(c))
