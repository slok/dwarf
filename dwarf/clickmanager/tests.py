import random
import calendar
import time

from django.test import TestCase
from django.conf import settings
from django.test.utils import override_settings
import redis

from linkshortener import utils
from linkshortener.models import ShortLink
from clickmanager.models import Click
from clickmanager.exceptions import ClickError, ClickNotFoundError
from clickmanager import tasks


def get_redis_connection():
    return redis.StrictRedis(connection_pool=settings.REDIS_POOL)


class ClickModelTest(TestCase):

    def tearDown(self):
        r = get_redis_connection()
        r.flushdb()

    def test_click_basic_object(self):
        token = utils.counter_to_token(random.randrange(0, 100000))
        click_id = random.randrange(0, 100000)
        OS = "linux"
        browser = "firefox"
        ip = "111.222.333.444"
        click_date = calendar.timegm(time.gmtime())
        language = "EN_us"
        location = "US"

        c = Click(click_id, token, ip, OS, browser, click_date, language,
                    location)

        #Check getters
        self.assertEquals(token, c.token)
        self.assertEquals(click_id, c.click_id)
        self.assertEquals(OS, c.os)
        self.assertEquals(browser, c.browser)
        self.assertEquals(ip, c.ip)
        self.assertEquals(click_date, c.click_date)
        self.assertEquals(language, c.language)
        self.assertEquals(location, c.location)

        #Check setters
        c2 = Click()
        c2.token = token
        c2.click_id = click_id
        c2.os = OS
        c2.browser = browser
        c2.ip = ip
        c2.click_date = click_date
        c2.language = language
        c2.location = location

        self.assertEquals(token, c2.token)
        self.assertEquals(click_id, c2.click_id)
        self.assertEquals(OS, c2.os)
        self.assertEquals(browser, c2.browser)
        self.assertEquals(ip, c2.ip)
        self.assertEquals(click_date, c2.click_date)
        self.assertEquals(language, c2.language)
        self.assertEquals(location, c2.location)

    def test_click_basic_object_str(self):
        token = utils.counter_to_token(random.randrange(0, 100000))
        click_id = random.randrange(0, 100000)
        OS = "linux"
        browser = "firefox"
        ip = "111.222.333.444"
        click_date = calendar.timegm(time.gmtime())
        language = "EN_us"
        location = "US"

        c = Click(click_id, token, ip, OS, browser, click_date, language,
                    location)

        format = Click.OBJECT_STR_FORMAT.format(click_id, token, ip, OS,
                                        browser, click_date, language, location)

        self.assertEquals(format, str(c))

    def test_click_basic_object_cmp(self):
        clicks = []

        for i in range(3):
            c = Click(token=i, click_id=i)
            clicks.append(c)

        c2 = Click(token=clicks[0].token, click_id=clicks[0].click_id)

        self.assertEquals(c2, clicks[0])
        self.assertNotEquals(clicks[0], clicks[1])
        self.assertLess(clicks[0], clicks[2])
        self.assertGreater(clicks[2], clicks[1])

    def test_click_store(self):
        token = utils.counter_to_token(random.randrange(0, 100000))
        click_id = random.randrange(0, 100000)
        OS = "linux"
        browser = "firefox"
        ip = "111.222.333.444"
        click_date = calendar.timegm(time.gmtime())
        language = "EN_us"
        location = "US"

        c = Click(click_id, token, ip, OS, browser, click_date, language,
                    location)

        c.save()

        # Check the stored object
        key = Click.REDIS_CLICK_KEY.format(token, click_id)
        r = get_redis_connection()
        values = r.hgetall(key)

        self.assertEquals(OS, values['os'])
        self.assertEquals(browser, values['browser'])
        self.assertEquals(ip, values['ip'])
        self.assertEquals(click_date, int(values['click_date']))
        self.assertEquals(language, values['language'])
        self.assertEquals(location, values['location'])

    def test_click_store_error(self):
        c = Click()
        self.assertRaises(ClickError, c.save)

    def test_click_store_autofields(self):

        token = utils.counter_to_token(random.randrange(0, 100000))
        url = "http://xlarrakoetxea.org"
        OS = "linux"
        ip = "111.222.333.444"
        incr_times = 4

        #Store a link
        sl = ShortLink(token=token, url=url)
        sl.save()

        for i in range(incr_times):
            ShortLink.incr_clicks(token)

        c = Click(token=token, os=OS, ip=ip)

        c.save()

        #The save method has set the click_date
        click_date = c.click_date
        self.assertIsNotNone(click_date)

         # Check the stored object
        key = Click.REDIS_CLICK_KEY.format(token, c.click_id)
        r = get_redis_connection()
        values = r.hgetall(key)

        # Check the key is correctly set (this means that the counter has
        # increased correctly)
        correct_key = Click.REDIS_CLICK_KEY.format(token, incr_times + 1)
        self.assertEquals(correct_key, key)

        self.assertEquals(OS, values['os'])
        self.assertEquals(ip, values['ip'])

    def test_click_find(self):
        token = utils.counter_to_token(random.randrange(0, 100000))
        OS = "linux"
        ip = "111.222.333.444"
        browser = "firefox"
        click_date = calendar.timegm(time.gmtime())
        language = "EN_us"
        location = "US"
        url = "http://xlarrakoetxea.org"

        sl = ShortLink(token=token, url=url)
        sl.save()

        c = Click(token=token, os=OS, ip=ip, browser=browser,
                click_date=click_date, language=language, location=location)
        c.save()

        c2 = Click.find(token, c.click_id)
        self.assertEquals(c, c2)

    def test_click_find_error(self):
        self.assertRaises(ClickError, Click.find, None, None)

    def test_click_find_not_found_error(self):
        something = random.randrange(0, 100000)
        self.assertRaises(ClickNotFoundError, Click.find, something, something)

    def test_click_findall(self):
        url = "http://xlarrakoetxea.org"
        clicks = set()

        # Save
        sl = ShortLink(url=url)
        sl.save()

        # Clicks
        for i in range(random.randrange(0, 5)):
            c = Click(token=sl.token, os="linux")
            c.save()
            clicks.add(c)

        clicks2 = Click.findall(sl.token)

        self.assertEquals(len(clicks), len(clicks2))

        for i in clicks:
            clicks2_aux = set(clicks2)
            for j in clicks2_aux:
                if i == j:
                    clicks2.remove(j)

        self.assertEquals(0, len(clicks2))

    def test_click_findall_error(self):
        self.assertRaises(ClickError, Click.findall, None)

    def test_click_findall_not_found_error(self):
        something = random.randrange(0, 100000)
        self.assertRaises(ClickNotFoundError, Click.findall, something)


# Override testing settings in 1.4, run task test without workers
# http://docs.celeryproject.org/en/latest/configuration.html#celery-always-eager
@override_settings(CELERY_ALWAYS_EAGER=True)
class ClickTasksTest(TestCase):

    def tearDown(self):
        r = get_redis_connection()
        r.flushdb()

    def test_click_link(self):

        data = {'LANG': "en_US",
            'REMOTE_ADDR': "127.0.0.1",
            'HTTP_USER_AGENT': "Mozilla/5.0 (X11; Linux x86_64; rv:17.0)" +\
                                " Gecko/17.0 Firefox/17.0"}

        # Prepare the database
        counter = random.randrange(0, 100000)
        url = "http://xlarrakoetxea.org"
        sl = ShortLink(counter=counter, url=url)
        sl.save()

        # Call teh task
        result = tasks.click_link.delay(sl.token, data)
        # Wait (for testing only)
        result.get()

        # Check the stored information
        c = Click.find(sl.token, 1)

        self.assertEquals("en_US", c.language)
        self.assertEquals("linux x86_64", c.os)
        self.assertEquals("firefox", c.browser)
        self.assertEquals("127.0.0.1", c.ip)
