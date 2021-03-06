from django.db import models
from django.contrib.auth.models import User

from exceptions import ShortLinkError, ShortLinkNotFoundError
from linkshortener.utils import counter_to_token, token_to_counter
from dwarfutils import dateutils
from dwarfutils.redisutils import get_redis_connection


# This is a Django model
class UserLink(models.Model):
    user = models.ForeignKey(User)
    token = models.CharField(max_length=100)

    def __unicode__():
        return "{0}:{1}".format(user.username, token)


# This is a Redis model
class ShortLink(object):
    """Model of a short link that represents a link in the database. This link
    has the link iself, the id number assigned and the id number translation to
    the token that will use the shortened links
    """

    # Class variables
    REDIS_COUNTER_KEY = "ShortLink:counter"
    REDIS_TOKEN_KEY = "ShortLink:{0}"
    REDIS_URL_KEY = "ShortLink:{0}:tokens"
    OBJECT_STR_FORMAT = "[<{0}> <{1}> <{2}> <{3}> <{4}> <{5}> <{6}> <{7}>]"

    def __init__(self, counter=None, url=None, token=None, creation_date=None,
                    clicks=0, title=None, host=None):
        """Constructor of the class. The counter has priority. If you pass the
        counter and the token to the constructor (not only on of them) then the
        token will be ignored because with the counter we translate to generate
        the token also

        :param counter: The counter to translate the token
        :param token: The token assigned to the url (will translate to counter)
        :param url: The url identified by the token
        :param creation_date: The link creation date (UNIX UTC/GMT format)
        :param clicks: The clicks of the link
        :param title: The title of the link
        :param host: The host of the link
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
        self._clicks = clicks
        self._title = title
        self._host = host
        self._disabled = False
        # UNIX format UTC/GMT
        #self._creation_date = calendar.timegm(time.gmtime())
        self._creation_date = creation_date

    def __str__(self):
        """String representation of a shortLink object"""

        return ShortLink.OBJECT_STR_FORMAT.format(self._counter,
                                                self.token,
                                                self.url,
                                                self._creation_date,
                                                self._clicks,
                                                self._title,
                                                self._host,
                                                self._disabled)

    def __cmp__(self, other):
        """Comparation method of links, equals, lesser and greater"""

        if self.counter == other.counter and\
            self.token == other.token and\
            self.url == other.url and\
            self.creation_date == other.creation_date and\
            self.clicks == other.clicks and\
            self.title == other.title and\
            self.host == other.host and\
            self.disabled == other.disabled:
            return 0
        elif self.counter < other.counter:
                return -1
        elif self.counter > other.counter:
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
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value

    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, value):
        self._host = value

    @property
    def creation_date(self):
        return self._creation_date

    @creation_date.setter
    def creation_date(self, value):
        self._creation_date = value

    @property
    def disabled(self):
        return self._disabled

    @disabled.setter
    def disabled(self, value):
        self._disabled = value

    def _find_by_token(self):
        """Private method that searches a shortlink in the database by it's
        token and returns a ShortLink redis raw data.
        In this case returns a list with [url, creation_date, clicks]"""

        r = get_redis_connection()
        return r.hgetall(ShortLink.REDIS_TOKEN_KEY.format(self.token))

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
        if counter is not None:
            aux_self.counter = counter
            aux_self.token = counter_to_token(counter)
            data = aux_self._find_by_token()
            #Not found...

            if not data:
                raise ShortLinkNotFoundError("Short link not found")

            aux_self.url = data.get('url')
            aux_self.creation_date = int(data.get('creation_date', 0))
            aux_self.clicks = int(data.get('clicks', 0))
            aux_self.title = data.get('title')
            aux_self.host = data.get('host')
            aux_self.disabled = True if int(data.get('disabled')) else False

            return aux_self

        elif token is not None:
            aux_self.token = token
            aux_self.counter = token_to_counter(token)
            data = aux_self._find_by_token()

            #Not found...
            if not data:
                raise ShortLinkNotFoundError("Short link not found")

            aux_self.url = data.get('url')
            aux_self.creation_date = int(data.get('creation_date', 0))
            aux_self.clicks = int(data.get('clicks', 0))
            aux_self.title = data.get('title')
            aux_self.host = data.get('host')
            aux_self.disabled = True if int(data.get('disabled')) else False

            return aux_self
        elif url:
            aux_self.url = url
            tokens = aux_self._find_by_url()

            #Not found...
            if not tokens:
                ShortLinkNotFoundError("Short links not found")

             #Check again (maybe we have a list with all Nones)
            nothing = True
            for i in tokens:
                if i:
                    nothing = False
                    break

            if nothing:
                raise ShortLinkNotFoundError("Short link not found")

            short_links = []
            for i in tokens:
                aux_self.token = i
                data = aux_self._find_by_token()
                sl = ShortLink()
                sl.token = i
                sl.url = data.get('url')
                sl.creation_date = int(data.get('creation_date', 0))
                sl.clicks = int(data.get('clicks', 0))
                sl.title = data.get('title')
                sl.host = data.get('host')
                #aux_self.title = data.get('title')
                #aux_self.host = data.get('host')
                sl.disabled = True if int(data.get('disabled')) else False
                short_links.append(sl)
            return short_links

        raise ShortLinkError("No enought data to search")

    @classmethod
    def findall(cls):
        """Returns all the shortlinks in the database"""

        #If there isn't nothing this will raise exception
        total = ShortLink.get_counter()

        sls = []
        for i in range(1, total + 1):
            sls.append(ShortLink.find(counter=i))

        return sls

    def save(self):
        """Saves or updates the ShortLink instance in database"""

        if not self.url:
            raise ShortLinkError("Token or url are empty")

        r = get_redis_connection()

        #If not token or counter then we need to get the apropiate one (last)
        if not self.token and not self.counter:
            self.counter = ShortLink.incr_counter()

        # Do all in pipeline
        pipe = r.pipeline()

        # Save token(Hash) and url(set)

        #If there is not a date then take now
        if not self.creation_date:
            self.creation_date = dateutils.unix_now_utc()

        disabled = 1 if self.disabled else 0

        mappings = {'url': self.url,
                'creation_date': self.creation_date,
                'clicks': self.clicks,
                'title': self.title,
                'host': self.host,
                'disabled': disabled}

        pipe.hmset(ShortLink.REDIS_TOKEN_KEY.format(self.token), mappings)
        pipe.sadd(ShortLink.REDIS_URL_KEY.format(self.url), self.token)

        return pipe.execute()

    def disable(self):

        r = get_redis_connection()
        key = ShortLink.REDIS_TOKEN_KEY.format(self.token)
        self.disabled = True
        r.hset(key, "disabled", 1)

    def enable(self):
        r = get_redis_connection()
        key = ShortLink.REDIS_TOKEN_KEY.format(self.token)
        self.disabled = False
        r.hset(key, "disabled", 0)

    def delete(self):
        lua_script = """
            local token = ARGV[1]

            --Delete all the data
            --Clicks
            local i = 0
            local result = 1
            while result > 0 do
                i = i + 1
                result = redis.call('del',KEYS[3] .. tostring(i))
            end

            --Token
            redis.call('del',KEYS[1])
            return redis.call('srem',KEYS[2], token)
        """

        r = get_redis_connection()
        delete = r.register_script(lua_script)

        token_key = ShortLink.REDIS_TOKEN_KEY.format(self.token)
        url_key = ShortLink.REDIS_URL_KEY.format(self.url)
        #Circular dependency destroyer!
        from clickmanager.models import Click
        click_key = Click.REDIS_CLICK_KEY.format(self.token, "")

        delete(keys=[token_key, url_key, click_key], args=[self.token, ])

    @classmethod
    def get_counter(cls):
        """Gets the global counter of links stored in database"""

        r = get_redis_connection()
        key = ShortLink.REDIS_COUNTER_KEY

        if not r.exists(key):
            r.set(key, 0)  # Initialize the counter

        return int(r.get(key))

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

    @classmethod
    def _incr_decr_clicks(cls, token, value):
        """Increments/decrements the clicks of short link and returns the
        new counter incremented"""

        r = get_redis_connection()
        key = ShortLink.REDIS_TOKEN_KEY.format(token)

        if not r.exists(key):
            raise ShortLinkNotFoundError("Token doesn't exists")

        return r.hincrby(key, 'clicks', value)

    @classmethod
    def incr_clicks(cls, token):
        """Increments the clicks of short link and returns the new counter
        incremented"""

        return ShortLink._incr_decr_clicks(token, 1)

    @classmethod
    def decr_clicks(cls, token):
        """Decrements the clicks of short link and returns the new counter
        incremented"""

        return ShortLink._incr_decr_clicks(token, -1)
