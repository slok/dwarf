from django.conf import settings
import redis

from linkshortener.models import ShortLink
from linkshortener.exceptions import ShortLinkNotFoundError
from clickmanager.exceptions import ClickError, ClickNotFoundError
from dwarfutils import dateutils


def get_redis_connection():
    return redis.StrictRedis(connection_pool=settings.REDIS_POOL)


class Click(object):
    """ This model represent a single click instance with all its information
    for storing in a database
    """

    # Class variables
    REDIS_CLICK_KEY = "Click:{0}:{1}"
    OBJECT_STR_FORMAT = "[<{0}> <{1}> <{2}> <{3}> <{4}> <{5}> <{6}> <{7}>]"
    FIELDS = ("click_id", "token", "ip", "os", "browser", "click_date",
            "language", "location")

    def __init__(self, click_id=None, token=None, ip=None, os=None,
                browser=None, click_date=None, language=None, location=None):

        self._click_id = click_id
        self._token = token
        self._ip = ip
        self._os = os
        self._browser = browser
        self._click_date = click_date
        self._language = language
        self._location = location

    def __str__(self):
        """String representation of a Click object"""

        return Click.OBJECT_STR_FORMAT.format(self._click_id,
                                                self._token,
                                                self._ip,
                                                self._os,
                                                self._browser,
                                                self._click_date,
                                                self._language,
                                                self._location)

    def __cmp__(self, other):
        """Comparation method of clicks, equals, lesser and greater"""

        if self.token == other.token and\
            self.click_id == other.click_id and\
            self.ip == other.ip and\
            self.os == other.os and\
            self.click_date == other.click_date and\
            self.language == other.language and\
            self.location == other.location and\
            self.browser == other.browser:
            return 0
        elif self.click_id < other.click_id:
                return -1
        elif self.click_id > other.click_id:
                return 1

        raise ClickError("Not enought data in object to compare")

    @property
    def click_id(self):
        return self._click_id

    @click_id.setter
    def click_id(self, value):
        self._click_id = value

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, value):
        self._token = value

    @property
    def ip(self):
        return self._ip

    @ip.setter
    def ip(self, value):
        self._ip = value

    @property
    def os(self):
        return self._os

    @os.setter
    def os(self, value):
        self._os = value

    @property
    def browser(self):
        return self._browser

    @browser.setter
    def browser(self, value):
        self._browser = value

    @property
    def click_date(self):
        return self._click_date

    @click_date.setter
    def click_date(self, value):
        if not isinstance(value, int):
            value = int(value)
        self._click_date = value

    @property
    def language(self):
        return self._language

    @language.setter
    def language(self, value):
        self._language = value

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, value):
        self._location = value

    def save(self):
        """ Save a click in the database. If the instance doens't have the 
        click_id the method will get the correct value, based on the Short link
        click counter"""

        r = get_redis_connection()

        if not self.token:
            raise ClickError("Not enought data to store click instance")

        #if there isn't an identification then get the apropiate id
        if not self.click_id:
            self.click_id = ShortLink.incr_clicks(self.token)

        #set the date if there isn't a date
        if not self.click_date:
            self.click_date = dateutils.unix_now_utc()

        key = Click.REDIS_CLICK_KEY.format(self.token, self.click_id)

        #Create the data
        to_store = {}
        for i in Click.FIELDS:
            value = getattr(self, i)
            if value:
                to_store[i] = value

        r.hmset(key, to_store)

    @classmethod
    def find(cls, token, click_id):
        """Finds a click based on the token and clicks id (incremental id)

        :param token: the token that represents the clicks
        :param click_id: the id that represents a (unique with the token) click
        """

        if not token or not click_id:
            raise ClickError("Not enought data to find a Click instance")

        #Prepare de key (our query :P)
        key = Click.REDIS_CLICK_KEY.format(token, click_id)
        r = get_redis_connection()

        #Get values from the database
        values = r.hgetall(key)

        if not values:
            raise ClickNotFoundError()
        else:
            #Get values
            c = Click()
            for i in Click.FIELDS:
                try:
                    value = values.get(i)
                    setattr(c, i, value)
                #Doesn't exist the value, so None (not use the setter)
                except AttributeError:
                    pass
            #Now set the token and the click_id
            c.token = token
            c.click_id = click_id

            return c

    @classmethod
    def findall(cls, token):
        """Finds all the click instances of a given token. Returns a set of
        Click instances

        :param token: the token that is associated to the clicks
        """

        if not token:
            raise ClickError("Not enought data to find a Click instance")

        # Get the max counters
        counter = 0
        try:
            short_link = ShortLink.find(token=token)
            counter = short_link.clicks
        except ShortLinkNotFoundError:
            raise ClickNotFoundError("Shortlink doesnt exists, clicks neither")

        clicks = set()
        for i in range(1, counter + 1):
            clicks.add(Click.find(token, i))

        return clicks
