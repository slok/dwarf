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

    def __init__(self):
        self._counter = None
        self._token = None
        self._url = None
        self._friends = None

    def __str__(self):
        return "[<{0}> <{1}> <{2}>]".format(self._counter, self.token, self.url)

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
        return r.get(self.token)

    def _find_by_url(self):
        raise NotImplementedError

    @classmethod
    def find(counter=None, token=None, url=None):
        aux_self = ShortLink()
        if token:
            aux_self.token = token
            aux_self._counter = token_to_counter(token)
            aux_self.url = aux_self._find_by_token()
        else:
            raise NotImplementedError

    def save(self):

        if not self.token or not self.url:
            raise ShortLinkError("Token or url are empty")

        r = get_redis_connection()

        # Do all in pipeline
        pipe = r.pipeline()

        # Save token and url
        pipe.set(ShortLink.REDIS_TOKEN_KEY.format(self.token), self.url)
        pipe.set(ShortLink.REDIS_URL_KEY.format(self.url), self.token)

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
