import random

from django.test import TestCase
from django.conf import settings
from django.test.utils import override_settings
from django.contrib.auth.models import User
import redis

from linkshortener import utils
from linkshortener.exceptions import (LinkShortenerLengthError, ShortLinkError,
                                      ShortLinkNotFoundError)
from linkshortener.models import ShortLink, UserLink
from linkshortener import tasks
from dwarfutils import dateutils
from dwarfutils.redisutils import get_redis_connection
from clickmanager.models import Click


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
        title = "This is a title"
        host = url
        disabled = True

        format = ShortLink.OBJECT_STR_FORMAT.format(counter,
                                                token,
                                                url,
                                                creation_date,
                                                clicks,
                                                title,
                                                host,
                                                disabled)

        sl = ShortLink(counter=counter, url=url, title=title, host=host)
        sl.disabled = disabled

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
        title = "This is a title"
        host = url
        disabled = True

        # Setters from counter
        sl = ShortLink(counter=counter, url=url, title=title, host=host)
        sl.disabled = disabled

        # Getters
        self.assertEquals(url, sl.url)
        self.assertEquals(counter, sl.counter)
        self.assertEquals(token, sl.token)
        self.assertEquals(creation_date, sl.creation_date)
        self.assertEquals(clicks, sl.clicks)
        self.assertEquals(title, sl.title)
        self.assertEquals(host, sl.host)
        self.assertEquals(disabled, sl.disabled)

        # Setters from token
        sl2 = ShortLink(token=token, url=url)
        creation_date = dateutils.unix_now_utc()
        sl2.creation_date = creation_date
        clicks = 5
        sl2.clicks = clicks
        sl2.title = title
        sl2.host = host
        sl2.disabled = disabled

        # Getters
        self.assertEquals(url, sl2.url)
        self.assertEquals(counter, sl2.counter)
        self.assertEquals(token, sl2.token)
        self.assertEquals(creation_date, sl2.creation_date)
        self.assertEquals(clicks, sl2.clicks)
        self.assertEquals(title, sl2.title)
        self.assertEquals(host, sl2.host)
        self.assertEquals(disabled, sl2.disabled)

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
        creation_date = dateutils.unix_now_utc()
        clicks = 20
        title = "This is a title"
        host = url
        disabled = True

        # Save the links
        sl = ShortLink(counter=counter, url=url, creation_date=creation_date,
                        clicks=clicks, title=title, host=host)
        sl.disabled = disabled
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
        keys = ('url', 'creation_date', 'clicks', 'title', 'host')
        data = [url, creation_date, clicks, title, host]
        aux = r.hmget(rtk, keys)

        data_result = [aux[0], int(aux[1]), int(aux[2]), aux[3], aux[4]]
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
        title = "My webpage"
        host = "xlarrakoetxea.org"

        # Set the shor link counter
        for i in range(times):
            ShortLink.incr_counter()

        # Save
        sl = ShortLink()
        sl.url = url
        sl.title = title
        sl.host = host
        sl.save()

        # Check the correct counter
        sl2 = ShortLink.find(counter=times + 1)
        self.assertEquals(sl, sl2)

    def test_get_shortLink_by_counter(self):
        counter = random.randrange(0, 100000)
        url = "xlarrakoetxea.org"
        title = "My webpage"
        host = "xlarrakoetxea.org"

        sl = ShortLink(counter=counter, url=url, title=title, host=host)
        sl.save()

        sl2 = ShortLink.find(counter=counter)

        self.assertEquals(sl, sl2)

    def test_get_shortLink_by_token(self):
        counter = random.randrange(0, 100000)
        url = "xlarrakoetxea.org"
        title = "My webpage"
        host = "xlarrakoetxea.org"

        sl = ShortLink(token=utils.counter_to_token(counter), url=url, title=title, host=host)
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

    def test_getall_shortlink(self):
        times = random.randrange(1, 20)

        for i in range(times):
            url = "xlarrakoetxea{0}.org".format(i)
            sl = ShortLink(url=url)
            sl.save()

        sls = ShortLink.findall()
        self.assertEquals(times, len(sls))

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

    def test_disable_link(self):
        clicks = random.randrange(0, 100000)
        counter = random.randrange(0, 100000)
        url = "xlarrakoetxea.org"

        sl = ShortLink(counter=counter, url=url, clicks=clicks)
        sl.save()

        sl.disable()

        #Find
        sl2 = ShortLink.find(token=sl.token)
        self.assertTrue(sl2.disabled)

    def test_enable_link(self):
        clicks = random.randrange(0, 100000)
        counter = random.randrange(0, 100000)
        url = "xlarrakoetxea.org"

        sl = ShortLink(counter=counter, url=url, clicks=clicks)
        sl.save()

        sl.disable()

        sl2 = ShortLink.find(token=sl.token)
        self.assertTrue(sl2.disabled)

        sl2.enable()
        sl2 = ShortLink.find(token=sl.token)
        self.assertFalse(sl2.disabled)

    def test_delete_link(self):
        counter = random.randrange(0, 100000)
        url = "xlarrakoetxea.org"

        sl = ShortLink(counter=counter, url=url)
        sl.save()

        r = get_redis_connection()

        times = random.randrange(10, 100)

        for i in range(times):
            c = Click(token=sl.token)
            c.save()

        self.assertTrue(r.exists(ShortLink.REDIS_TOKEN_KEY.format(sl.token)))
        self.assertTrue(r.sismember(ShortLink.REDIS_URL_KEY.format(sl.url),
                                    sl.token))
        self.assertEquals(times, len(r.keys(
                                Click.REDIS_CLICK_KEY.format(sl.token, "*"))))

        sl.delete()

        self.assertFalse(r.exists(ShortLink.REDIS_TOKEN_KEY.format(sl.token)))
        self.assertFalse(r.sismember(ShortLink.REDIS_URL_KEY.format(sl.url),
                                     sl.token))
        self.assertEquals(0, len(r.keys(
                                Click.REDIS_CLICK_KEY.format(sl.token, "*"))))


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
        
        # The host and title are set after the instance was created so we add
        sl2.host = sl.host
        sl2.title = sl.title

        self.assertEquals(sl2, sl)

    def test_create_new_token_with_user(self):
        counter = random.randrange(100000)
        url = "http://xlarrakoetxea{0}.org".format(random.randrange(100))

        # Set the counter
        ShortLink.set_counter(counter)

        # Create user
        user = User()
        user.username = "test"
        user.save()
        user_id = user.id

        # Call the async task with celery
        result = tasks.create_token.delay(url, user_id)
        new_token = result.get()

        #Check if the returned token is ok
        self.assertEquals(utils.counter_to_token(counter + 1), new_token)
        self.assertTrue(result.successful())

        # Check if the link is stored in the database correctly
        sl = ShortLink.find(url=url)[0]

        # creation_date is trap!! :P
        sl2 = ShortLink(counter=counter + 1, url=url,
                    creation_date=sl.creation_date)

        # The host and title are set after the instance was created so we add
        sl2.host = sl.host
        sl2.title = sl.title

        self.assertEquals(sl2, sl)

        user_link = UserLink.objects.get(user=user)
        self.assertEquals(sl.token, user_link.token)        
