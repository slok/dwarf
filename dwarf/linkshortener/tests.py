import random
import calendar
import time

from django.test import TestCase
from django.conf import settings
from django.test.utils import override_settings
import redis

from linkshortener import utils
from linkshortener.exceptions import (LinkShortenerLengthError, ShortLinkError,
                                    ShortLinkNotFoundError)
from linkshortener.models import ShortLink
from linkshortener import tasks


def get_redis_connection():
    return redis.StrictRedis(connection_pool=settings.REDIS_POOL)


class UtilTest(TestCase):

    def tearDown(self):
        r = get_redis_connection()
        r.flushdb()

    def test_first_shortened_url_token(self):
        next = utils.next_token()
        self.assertEquals("0000", next)

    def test_small_current_shortened_url_token(self):
        self.assertRaises(LinkShortenerLengthError, utils.next_token, "a")

    def test_next_shortened_url_token(self):
        test_data = (
                        ("0000", "0001"), ("0005", "0006"), ("0008", "0009"),
                        ("0009", "000a"), ("000b", "000c"), ("000o", "000p"),
                        ("000z", "000A"), ("000G", "000H"), ("000Y", "000Z"),
                        ("000Z", "0010"), ("34ZZ", "3500"), ("aabz", "aabA"),
                        ("a00z", "a00A"), ("Az3d", "Az3e"), ("YZZZ", "Z000"),
                    )

        for i in test_data:
            self.assertEquals(i[1], utils.next_token(i[0]))

    def test_next_shortened_url_token_limits(self):
        test_data = (
                        ("ZZZZZ", "100000"), ("ZZZZZZZZ", "100000000")
                    )

        for i in test_data:
            self.assertEquals(i[1], utils.next_token(i[0]))

    #Based on counter checks
    test_data = (
                        ("0000", 0), ("0005", 5), ("0006", 6), ("0009", 9),
                        ("000a", 10), ("000s", 28), ("000E", 40), ("000Z", 61),
                        ("0010", 62), ("001C", 100), ("0q0U", 100000),
                    )

    def test_start_counter_translation(self):
        counter = 0
        self.assertEquals("0000", utils.counter_to_token(counter))

    def test_counter_translation(self):
        for i in UtilTest.test_data:
            self.assertEquals(i[0], utils.counter_to_token(i[1]))

    def test_number_translation(self):

        for i in UtilTest.test_data:
            self.assertEquals(i[1], utils.token_to_counter(i[0]))


class ShortLinkModelTest(TestCase):

    def tearDown(self):
        r = get_redis_connection()
        r.flushdb()

    def test_shortlink_basic_object_str(self):
        url = "xlarrakoetxea.org"
        counter = random.randrange(0, 100000)
        token = utils.counter_to_token(counter)
        creation_date = None
        clicks = 0

        format = ShortLink.OBJECT_STR_FORMAT.format(counter,
                                                token,
                                                url,
                                                creation_date,
                                                clicks)

        sl = ShortLink(counter=counter, url=url)

        self.assertEquals(format, str(sl))

    def test_shortlink_basic_object_cmp(self):
        short_links = []

        for i in range(3):
            sl = ShortLink(counter=i, url="xlarrakoetxea.org")
            short_links.append(sl)

        sl = ShortLink(counter=short_links[0].counter, url=short_links[0].url)

        self.assertEquals(sl, short_links[0])
        self.assertNotEquals(short_links[0], short_links[1])
        self.assertLess(short_links[0], short_links[2])
        self.assertGreater(short_links[2], short_links[1])

    def test_shortlink_basic_object(self):
        url = "xlarrakoetxea.org"
        counter = random.randrange(0, 100000)
        token = utils.counter_to_token(counter)
        creation_date = None
        clicks = 0

        # Setters from counter
        sl = ShortLink(counter=counter, url=url)

        # Getters
        self.assertEquals(url, sl.url)
        self.assertEquals(counter, sl.counter)
        self.assertEquals(token, sl.token)
        self.assertEquals(creation_date, sl.creation_date)
        self.assertEquals(clicks, sl.clicks)

        # Setters from token
        sl2 = ShortLink(token=token, url=url)
        creation_date = calendar.timegm(time.gmtime())
        sl2.creation_date = creation_date
        clicks = 5
        sl2.clicks = clicks

        # Getters
        self.assertEquals(url, sl2.url)
        self.assertEquals(counter, sl2.counter)
        self.assertEquals(token, sl2.token)
        self.assertEquals(creation_date, sl2.creation_date)
        self.assertEquals(clicks, sl2.clicks)

    def test_stored_counter_set_get(self):
        counter = random.randrange(0, 100000)
        ShortLink.set_counter(counter)
        self.assertEquals(counter, ShortLink.get_counter())

    def test_increment_stored_counter(self):
        counter = random.randrange(0, 100000)
        times = random.randrange(0, 100)

        ShortLink.set_counter(counter)
        for i in range(times):
            self.assertEquals(counter + i + 1, ShortLink.incr_counter())
        self.assertEquals(counter + times, ShortLink.get_counter())

    def test_save_shortLink(self):
        counter = random.randrange(0, 100000)
        url = "xlarrakoetxea.org"
        creation_date = calendar.timegm(time.gmtime())
        clicks = 20
        # Save the links
        sl = ShortLink(counter=counter, url=url, creation_date=creation_date,
                        clicks=clicks)
        sl.save()

        r = redis.StrictRedis(host=settings.REDIS_HOST,
                             port=settings.REDIS_PORT,
                             db=settings.REDIS_DB)

        # Construct the Keys
        rtk = ShortLink.REDIS_TOKEN_KEY.format(utils.counter_to_token(counter))
        ruk = ShortLink.REDIS_URL_KEY.format(url)

        # Check
        token = utils.counter_to_token(counter)
        self.assertTrue(token in r.smembers(ruk))
        keys = ('url', 'creation_date', 'clicks')
        data = [url, creation_date, clicks]
        aux = r.hmget(rtk, keys)

        data_result = [aux[0], int(aux[1]), int(aux[2])]
        self.assertEquals(data, data_result)

    def test_save_shortLink_error(self):
        counter = random.randrange(0, 100000)
        sl = ShortLink()

        self.assertRaises(ShortLinkError, sl.save)

        sl.url = None
        sl.counter = counter
        self.assertRaises(ShortLinkError, sl.save)

    def test_save_shortLink_autofield(self):
        times = random.randrange(1, 100)
        url = "xlarrakoetxea.org"

        # Set the shor link counter
        for i in range(times):
            ShortLink.incr_counter()

        # Save
        sl = ShortLink()
        sl.url = url
        sl.save()

        # Check the correct counter
        sl2 = ShortLink.find(counter=times + 1)
        self.assertEquals(sl, sl2)

    def test_get_shortLink_by_counter(self):
        counter = random.randrange(0, 100000)
        url = "xlarrakoetxea.org"

        sl = ShortLink(counter=counter, url=url)
        sl.save()

        sl2 = ShortLink.find(counter=counter)

        self.assertEquals(sl, sl2)

    def test_get_shortLink_by_token(self):
        counter = random.randrange(0, 100000)
        url = "xlarrakoetxea.org"
        sl = ShortLink(token=utils.counter_to_token(counter), url=url)
        sl.save()

        sl2 = ShortLink.find(token=sl.token)

        self.assertEquals(sl, sl2)

    def test_get_shortLinks_by_url(self):
        times = 10
        counters = [random.randrange(0, 100000) for i in range(times)]
        url = "xlarrakoetxea.org"

        for i in counters:
            sl = ShortLink(counter=i, url=url)
            sl.save()

        sls = ShortLink.find(url=sl.url)

        self.assertEquals(len(counters), len(sls))

    def test_get_shortLink_not_found(self):
        something = random.randrange(0, 100000)
        self.assertRaises(ShortLinkNotFoundError, ShortLink.find,
                        something, None, None)

        self.assertRaises(ShortLinkNotFoundError, ShortLink.find,
                        None, something, None)

        self.assertRaises(ShortLinkNotFoundError, ShortLink.find,
                        None, None, something)

    def test_incr_clicks(self):
        clicks = random.randrange(0, 100000)
        counter = random.randrange(0, 100000)
        url = "xlarrakoetxea.org"

        sl = ShortLink(counter=counter, url=url, clicks=clicks)
        sl.save()

        #Increment
        result = ShortLink.incr_clicks(sl.token)

        #Increment manually the old one
        sl.clicks = sl.clicks + 1

        #Find
        sls = ShortLink.find(token=sl.token)

        self.assertEquals(sl.clicks, sls.clicks)
        self.assertEquals(result, sls.clicks)

    def test_decr_clicks(self):
        clicks = random.randrange(0, 100000)
        counter = random.randrange(0, 100000)
        url = "xlarrakoetxea.org"

        sl = ShortLink(counter=counter, url=url, clicks=clicks)
        sl.save()

        #decrement
        result = ShortLink.decr_clicks(sl.token)

        #decrement manually the old one
        sl.clicks = sl.clicks - 1

        #Find
        sls = ShortLink.find(token=sl.token)

        self.assertEquals(sl.clicks, sls.clicks)
        self.assertEquals(result, sls.clicks)

    def test_decr_incr_clicks_error(self):
        something = random.randrange(0, 100000)

        self.assertRaises(ShortLinkNotFoundError,
                    ShortLink.incr_clicks, something)

        self.assertRaises(ShortLinkNotFoundError,
                    ShortLink.decr_clicks, something)


# Override testing settings in 1.4, run task test without workers
# http://docs.celeryproject.org/en/latest/configuration.html#celery-always-eager
@override_settings(CELERY_ALWAYS_EAGER=True)
class ShortLinkTasksTest(TestCase):

    def tearDown(self):
        r = get_redis_connection()
        r.flushdb()

    def test_create_new_token(self):
        counter = random.randrange(100000)
        url = "http://xlarrakoetxea{0}.org".format(random.randrange(100))

        # Set the counter
        ShortLink.set_counter(counter)

        # Call the async task with celery
        result = tasks.create_token.delay(url)
        new_token = result.get()

        #Check if the returned token is ok
        self.assertEquals(utils.counter_to_token(counter + 1), new_token)
        self.assertTrue(result.successful())

        # Check if the link is stored in the database correctly
        sl = ShortLink.find(url=url)[0]

        # creation_date is trap!! :P
        sl2 = ShortLink(counter=counter + 1, url=url,
                    creation_date=sl.creation_date)

        self.assertEquals(sl2, sl)
