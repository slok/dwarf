from django.conf import settings
import redis

from exceptions import ShortLinkError
from utils import counter_to_token, token_to_counter


def get_redis_connection():
    return redis.StrictRedis(host=settings.REDIS_HOST,
                             port=settings.REDIS_PORT,
                             db=settings.REDIS_DB)


class ShortLink(object):

    REDIS_COUNTER_KEY = "linkshortener:urls:counter"
    REDIS_TOKEN_KEY = "ShortLink:{0}:token"
    REDIS_URL_KEY = "ShortLink:{0}:url"
    OBJECT_STR_FORMAT = "[<{0}> <{1}> <{2}>]"

    def __init__(self):
        self._counter = None
        self._token = None
        self._url = None

    def __str__(self):
        return ShortLink.OBJECT_STR_FORMAT.format(self._counter,
                                                self.token,
                                                self.url)

    def __cmp__(self, other):
        if self._counter == other._counter and\
            self._token == other._token and\
            self._url == other._url:
            return 0
        elif self._counter < other._counter:
                return -1
        elif self._counter > other._counter:
                return 1

        raise ShortLinkError("Not enought data in object to compare")

    @property
    def counter(self):
        return self._counter

    @counter.setter
    def counter(self, value):
        self._counter = value
        self._token = counter_to_token(value)

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, value):
        self._token = value
        self._counter = token_to_counter(value)

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, value):
        self._url = value

    def _find_by_token(self):
        r = get_redis_connection()
        return r.get(ShortLink.REDIS_TOKEN_KEY.format(self.token))

    def _find_by_url(self):
        r = get_redis_connection()
        return r.smembers(ShortLink.REDIS_URL_KEY.format(self.url))

    @classmethod
    def find(cls, counter=None, token=None, url=None):
        aux_self = ShortLink()
        if counter:
            aux_self.counter = counter
            aux_self.token = counter_to_token(counter)
            aux_self.url = aux_self._find_by_token()
            return aux_self
        elif token:
            aux_self.token = token
            aux_self.counter = token_to_counter(token)
            aux_self.url = aux_self._find_by_token()
            return aux_self
        elif url:
            aux_self.url = url
            tokens = aux_self._find_by_url()
            short_links = []
            for i in tokens:
                sl = ShortLink()
                sl.url = url
                sl.token = i
                short_links.append(sl)
            return short_links

        raise ShortLinkError("No enought data to search")

    def save(self):

        if not self.token or not self.url:
            raise ShortLinkError("Token or url are empty")

        r = get_redis_connection()

        # Do all in pipeline
        pipe = r.pipeline()

        # Save token(key) and url(set)
        pipe.set(ShortLink.REDIS_TOKEN_KEY.format(self.token), self.url)
        pipe.sadd(ShortLink.REDIS_URL_KEY.format(self.url), self.token)

        return pipe.execute()

    @classmethod
    def get_counter(cls):
        r = get_redis_connection()
        return int(r.get(ShortLink.REDIS_COUNTER_KEY))

    @classmethod
    def set_counter(cls, counter):
        r = get_redis_connection()
        r.set(ShortLink.REDIS_COUNTER_KEY, counter)

    @classmethod
    def incr_counter(cls):
        r = get_redis_connection()
        return r.incr(ShortLink.REDIS_COUNTER_KEY)

    @classmethod
    def decr_counter(cls):
        r = get_redis_connection()
        return r.decr(ShortLink.REDIS_COUNTER_KEY)
