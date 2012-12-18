import calendar
import time

from django.conf import settings
import redis

from exceptions import ShortLinkError
from utils import counter_to_token, token_to_counter


def get_redis_connection():
    return redis.StrictRedis(connection_pool=settings.REDIS_POOL)


class ShortLink(object):
    """Model of a short link that represents a link in the database. This link
    has the link iself, the id number assigned and the id number translation to
    the token that will use the shortened links
    """

    # Class variables
    REDIS_COUNTER_KEY = "linkshortener:urls:counter"
    REDIS_TOKEN_KEY = "ShortLink:{0}:token"
    REDIS_URL_KEY = "ShortLink:{0}:url"
    OBJECT_STR_FORMAT = "[<{0}> <{1}> <{2}> <{3}> <{4}>]"

    def __init__(self, counter=None, url=None, token=None, creation_date=None,
                    clicks=0):
        """Constructor of the class. The counter has priority. If you pass the
        counter and the token to the constructor (not only on of them) then the
        token will be ignored because with the counter we translate to generate
        the token also

        :param counter: The counter to translate the token
        :param token: The token assigned to the url (will translate to counter)
        :param url: The url identified by the token
        :param creation_date: The link creation date (UNIX UTC/GMT format)
        :param clicks: The clicks of the link
        """

        # Use the getters to do the convertion operation
        # If counter then the token is set by the counter setter
        if counter:
            self.counter = counter
        else:
            # If not counter then check token
            # (the setter sets the proper counter)
            if token:
                self.token = token
            else:
                self._token = token
                self._counter = counter

        self._url = url
        self.clicks = clicks
        # UNIX format UTC/GMT
        #self._creation_date = calendar.timegm(time.gmtime())
        self._creation_date = creation_date

    def __str__(self):
        """String representation of a shortLink object"""

        return ShortLink.OBJECT_STR_FORMAT.format(self._counter,
                                                self.token,
                                                self.url,
                                                self._creation_date,
                                                self._clicks)

    def __cmp__(self, other):
        """Comparation method of links, equals, lesser and greater"""

        if self._counter == other._counter and\
            self._token == other._token and\
            self._url == other._url and\
            self._creation_date == other._creation_date and\
            self._clicks == other._clicks:
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

    @property
    def clicks(self):
        return self._clicks

    @clicks.setter
    def clicks(self, value):
        self._clicks = value

    @property
    def creation_date(self):
        return self._creation_date

    @creation_date.setter
    def creation_date(self, value):
        self._creation_date = value

    def _find_by_token(self):
        """Private method that searches a shortlink in the database by it's
        token and returns a ShortLink redis raw data.
        In this case returns a list with [url, creation_date, clicks]"""

        r = get_redis_connection()
        return_keys = ('url', 'creation_date', 'clicks')
        return r.hmget(ShortLink.REDIS_TOKEN_KEY.format(self.token),
                    return_keys)

    def _find_by_url(self):
        """Private method that searches all the shortlinks in the database by
        their url and returns a list of ShortLink keys"""

        r = get_redis_connection()
        return r.smembers(ShortLink.REDIS_URL_KEY.format(self.url))

    @classmethod
    def find(cls, counter=None, token=None, url=None):
        """Finds a shortlink or various shortlinks based on the counter,
        token or url

        :param counter: The counter of the link (numeric id)
        :param token: The token calculated based on the counter id
        :param url: The url of the stored ShortLink
        """

        aux_self = ShortLink()
        if counter:
            aux_self.counter = counter
            aux_self.token = counter_to_token(counter)
            data = aux_self._find_by_token()
            aux_self.url = data[0]
            aux_self.creation_date = int(data[1])
            try:
                aux_self.clicks = int(data[2])
            except ValueError:
                aux_self.clicks = 0

            return aux_self
        elif token:
            aux_self.token = token
            aux_self.counter = token_to_counter(token)
            data = aux_self._find_by_token()
            aux_self.url = data[0]
            aux_self.creation_date = int(data[1])
            try:
                aux_self.clicks = int(data[2])
            except ValueError:
                aux_self.clicks = 0

            return aux_self
        elif url:
            aux_self.url = url
            tokens = aux_self._find_by_url()
            short_links = []
            for i in tokens:
                aux_self.token = i
                data = aux_self._find_by_token()
                sl = ShortLink()
                sl.token = i
                sl.url = data[0]
                sl.creation_date = int(data[1])
                try:
                    sl.clicks = int(data[2])
                except ValueError:
                    sl.clicks = 0
                short_links.append(sl)
            return short_links

        raise ShortLinkError("No enought data to search")

    def save(self):
        """Saves or updates the ShortLink instance in database"""

        if not self.token or not self.url:
            raise ShortLinkError("Token or url are empty")

        r = get_redis_connection()

        # Do all in pipeline
        pipe = r.pipeline()

        # Save token(Hash) and url(set)

        #If there is not a date then take now
        if not self.creation_date:
            self.creation_date = calendar.timegm(time.gmtime())
        mappings = {'url': self.url,
                'creation_date': self.creation_date,
                'clicks': self.clicks}

        pipe.hmset(ShortLink.REDIS_TOKEN_KEY.format(self.token), mappings)
        pipe.sadd(ShortLink.REDIS_URL_KEY.format(self.url), self.token)

        return pipe.execute()

    @classmethod
    def get_counter(cls):
        """Gets the global counter of links stored in database"""

        r = get_redis_connection()
        return int(r.get(ShortLink.REDIS_COUNTER_KEY))

    @classmethod
    def set_counter(cls, counter):
        """Sets the global counter of links stored in database"""

        r = get_redis_connection()
        r.set(ShortLink.REDIS_COUNTER_KEY, counter)

    @classmethod
    def incr_counter(cls):
        """Increments the counter and returns the new counter incremented"""

        r = get_redis_connection()
        return r.incr(ShortLink.REDIS_COUNTER_KEY)

    @classmethod
    def decr_counter(cls):
        """ Decrements the counter and returns the new counter incremented"""

        r = get_redis_connection()
        return r.decr(ShortLink.REDIS_COUNTER_KEY)
