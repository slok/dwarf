import random

from django.test import TestCase
from django.conf import settings
import redis

from linkshortener import utils
from linkshortener.exceptions import LinkShortenerLengthError, ShortLinkError
from linkshortener.models import ShortLink


class UtilTest(TestCase):

    def setUp(self):
        r = redis.StrictRedis(host=settings.REDIS_HOST,
                             port=settings.REDIS_PORT,
                             db=settings.REDIS_DB)
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
                        ("ZZZZZ", "000000"), ("ZZZZZZZZ", "000000000")
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

    def test_shortlink_basic_object_str(self):
        url = "xlarrakoetxea.org"
        counter = random.randrange(0, 100000)
        token = utils.counter_to_token(counter)

        format = ShortLink.OBJECT_STR_FORMAT.format(counter, token, url)

        sl = ShortLink()
        sl.counter = counter
        sl.url = url

        self.assertEquals(format, str(sl))

    def test_shortlink_basic_object_cmp(self):
        short_links = []

        for i in range(3):
            sl = ShortLink()
            sl.counter = i
            sl.url = "xlarrakoetxea.org"
            short_links.append(sl)

        sl = ShortLink()
        sl.counter = short_links[0].counter
        sl.url = short_links[0].url

        self.assertEquals(sl, short_links[0])
        self.assertNotEquals(short_links[0], short_links[1])
        self.assertLess(short_links[0], short_links[2])
        self.assertGreater(short_links[2], short_links[1])

    def test_shortlink_basic_object(self):
        url = "xlarrakoetxea.org"
        counter = random.randrange(0, 100000)
        token = utils.counter_to_token(counter)

        # Setters from counter
        sl = ShortLink()
        sl.counter = counter
        sl.url = url

        # Getters
        self.assertEquals(url, sl.url)
        self.assertEquals(counter, sl.counter)
        self.assertEquals(token, sl.token)

        # Setters from token
        sl2 = ShortLink()
        sl2.token = token
        sl2.url = url

        # Getters
        self.assertEquals(url, sl2.url)
        self.assertEquals(counter, sl2.counter)
        self.assertEquals(token, sl2.token)

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

        # Save the links
        sl = ShortLink()
        sl.url = url
        sl.counter = counter
        sl.save()

        r = redis.StrictRedis(host=settings.REDIS_HOST,
                             port=settings.REDIS_PORT,
                             db=settings.REDIS_DB)

        # Construct the Keys
        rtk = ShortLink.REDIS_TOKEN_KEY.format(utils.counter_to_token(counter))
        ruk = ShortLink.REDIS_URL_KEY.format(url)

        # Check
        self.assertEquals(url, r.get(rtk))
        self.assertEquals(counter, utils.token_to_counter(r.get(ruk)))

    def test_save_shortLink_error(self):
        counter = random.randrange(0, 100000)
        url = "xlarrakoetxea.org"
        sl = ShortLink()

        self.assertRaises(ShortLinkError, sl.save)

        sl.url = url
        self.assertRaises(ShortLinkError, sl.save)

        sl.url = None
        sl.counter = counter
        self.assertRaises(ShortLinkError, sl.save)

    def test_get_shortLink_by_counter(self):
        counter = random.randrange(0, 100000)
        url = "xlarrakoetxea.org"
        sl = ShortLink()
        sl.counter = counter
        sl.url = url
        sl.save()

        sl2 = ShortLink.find(counter=counter)

        self.assertEquals(sl, sl2)

    def test_get_shortLink_by_token(self):
        counter = random.randrange(0, 100000)
        url = "xlarrakoetxea.org"
        sl = ShortLink()
        sl.token = utils.counter_to_token(counter)
        sl.url = url
        sl.save()

        sl2 = ShortLink.find(token=sl.token)

        self.assertEquals(sl, sl2)
