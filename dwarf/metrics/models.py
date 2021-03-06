import random
from datetime import datetime

from dwarfutils.redisutils import get_redis_connection
from dwarfutils.dateutils import datetime_now_utc


class BitmapMetrics(object):
    """ This class is an abstract class that represents a redis bitmap for
    metrics.

    The mMetricsetrics are based on 1 and 0 values along a bitmap, each position
    of the bitmap represents something. Anexample could be:
        * position 1 is the user id 1, position 2 is the user id 2...
        * if the flag is up (1) means that the user has logged
        * if the flag is down (0) means tha the user hasn't logged in
    With this example we could set the users that logged in an specific moment
    for example each day of the month.

    To use this class, we only have to implement the way that the key is setted.
    for example in the constructor or in the setter of an attribute. The only
    important thing is that the class needs to know the key (self._key) at the
    moment where python talks to Redis, (save or retrieve)

    """

    FLAG_UP = 1
    FLAG_DOWN = 0

    OP_KEY = "bitmapops:{0}:{1}"

    def __init__(self, bitmap=None):
        self._bitmap = bitmap
        self._key = None

    @property
    def key(self):
        return self._key

    def set_flag(self, flag_position):
        r = get_redis_connection()
        r.setbit(self._key, flag_position, BitmapMetrics.FLAG_UP)

    def unset_flag(self, flag_position):
        r = get_redis_connection()
        r.setbit(self._key, flag_position, BitmapMetrics.FLAG_DOWN)

    def set_flags(self, flag_positions):
        r = get_redis_connection()
        pipe = r.pipeline()
        for i in flag_positions:
            pipe.setbit(self._key, i, BitmapMetrics.FLAG_UP)
        pipe.execute()

    def unset_flags(self, flag_positions):
        r = get_redis_connection()
        pipe = r.pipeline()
        for i in flag_positions:
            pipe.setbit(self._key, i, BitmapMetrics.FLAG_DOWN)
        pipe.execute()

    def get_flag(self, flag_position):
        r = get_redis_connection()
        return r.getbit(self._key, flag_position)

    def get_flags(self, flag_positions):
        r = get_redis_connection()
        pipe = r.pipeline()
        for i in flag_positions:
            pipe.getbit(self._key, i)
        return pipe.execute()

    @classmethod
    def and_operation(cls, keys, store_key=None):
        """Makes an AND operation with all the redis keys.
        Returns the key on redis where the operation is stored
        (Creates a random key if no store key is passed)

        :param keys: The list of redis keys of the values for the AND operation
        """
        if not store_key:
            rand_id = random.randrange(0, 10000)
            store_key = BitmapMetrics.OP_KEY.format("and", rand_id)

        r = get_redis_connection()
        r.bitop("and", store_key, *keys)
        return store_key

    @classmethod
    def or_operation(cls, keys, store_key=None):
        """Makes an OR operation with all the redis keys.
        Returns the key on redis where the operation is stored

        :param keys: The list of redis keys of the values for the OR operation
        """
        if not store_key:
            rand_id = random.randrange(0, 10000)
            store_key = BitmapMetrics.OP_KEY.format("or", rand_id)

        r = get_redis_connection()
        r.bitop("or", store_key, *keys)
        return store_key

    @classmethod
    def xor_operation(cls, keys, store_key=None):
        """Makes an XOR operation with all the redis keys.
        Returns the key on redis where the operation is stored

        :param keys: The list of redis keys of the values for the XOR operation
        """
        if not store_key:
            rand_id = random.randrange(0, 10000)
            store_key = BitmapMetrics.OP_KEY.format("xor", rand_id)

        r = get_redis_connection()
        r.bitop("xor", store_key, *keys)
        return store_key

    @classmethod
    def not_operation(cls, key, store_key=None):
        """Makes an NOT operation In the bitmap of the redis key.
        Returns the key on redis where the operation is stored

        :param key: The redis key of the value for the NOT operation
        """
        if not store_key:
            rand_id = random.randrange(0, 10000)
            store_key = BitmapMetrics.OP_KEY.format("not", rand_id)

        r = get_redis_connection()
        r.bitop("not", store_key, key)
        return store_key

    @classmethod
    def check_flag(cls, key, position):
        """Checks a bit in the bitmap in the redis databases
        :param key: The key of redis where the bitmap resides
        :param position: The bitmap position to check
        """
        r = get_redis_connection()
        return r.getbit(key, position)

    @classmethod
    def count_flags(cls, key):
        """Counts all the flags activated in a given key (containing a bitmap)
        :param key: the key where the bitmap resides
        """
        r = get_redis_connection()
        return r.bitcount(key)


class AchievementMetrics(BitmapMetrics):
    """ Achievement Metrics for users"""

    def __init__(self, achievement_id, bitmap=None):
        super(AchievementMetrics, self).__init__(bitmap=bitmap)

        self._METRICS_KEY = "Metrics:achievements:{0}"
        self._achievement_id = achievement_id
        self._key = self._METRICS_KEY.format(self.achievement_id)

    @property
    def achievement_id(self):
        return self._achievement_id

    @achievement_id.setter
    def achievement_id(self, value):
        self._achievement_id = value
        self._key = self._METRICS_KEY.format(self._achievement_id)

    def user_has_achievement(self, user_id):
        return self.get_flag(user_id)

    def add_user_achievement(self, user_id):
        self.set_flag(user_id)

    def remove_user_achievement(self, user_id):
        self.unset_flag(user_id)

    def total_users(self):
        return self.__class__.count_flags(self._key)


class BitmapTimeMetrics(BitmapMetrics):
    """ Abstract Bitmap Metrics  in time """

    def __init__(self, metrics_date=None, bitmap=None,  metrics_key_format=None,
                 date_format=None):
        super(BitmapTimeMetrics, self).__init__(bitmap=bitmap)

        self._METRICS_KEY = metrics_key_format
        self._DATE_FORMAT = date_format  # Use Standard ISO-8601

        if not metrics_date:
            metrics_date = datetime_now_utc()
        self._metrics_date = metrics_date

        time = self._metrics_date.strftime(self._DATE_FORMAT)
        key = self._METRICS_KEY.format(time)

        self._key = key

    @property
    def metrics_date(self):
        return self._metrics_date

    @metrics_date.setter
    def metrics_date(self, value):
        self.metrics_date = value
        time = self.metrics_date.strftime(self._DATE_FORMAT)
        self._key = self._METRICS_KEY.format(time)

    def total_counts_per_hours(self):
        """ Returns a list from 0 to 23 with the counts for each hour"""

        results = []

        for i in range(24):
            date = datetime(year=self.metrics_date.year,
                            month=self.metrics_date.month,
                            day=self.metrics_date.day,
                            hour=i).strftime(self._DATE_FORMAT)
            key = self._METRICS_KEY.format(date)

            results.append(self.count_flags(key))

        return results

    def total_counts_per_day(self):
        """ Returns the count of the day"""
        return sum(self.total_counts_per_hours())


class LoginMetrics(BitmapTimeMetrics):
    """Bitmap metrics for  the users that have been logged in a certain
    moment in time.

        * bitmap flag 1 represents that a user has logged in
        * bitmap flag 0 represents that a user hasen't logged yet
        * the position of the bitmap represents the user id
    """
    def __init__(self,
                 metrics_date=None,
                 bitmap=None,
                 metrics_key_format="Metrics:login:{0}",
                 date_format="%Y-%m-%dT%H"):

        super(LoginMetrics, self).__init__(
                                        metrics_date=metrics_date,
                                        bitmap=bitmap,
                                        metrics_key_format=metrics_key_format,
                                        date_format=date_format)

    def save_user_login(self, user_id):
        if not self.metrics_date:
            raise AttributeError("Datetime is needed")
        self.set_flag(user_id)

    def save_users_login(self, users_ids):
        if not self.metrics_date:
            raise AttributeError("Datetime is needed")
        self.set_flags(users_ids)

    def count_hours_logins(self):
        return self.total_counts_per_hours()
#--------------


class CounterMetrics(object):
    """ Abstract class for metrics represented by counts, this means that the
    representation of the metrics is done by a counter
    """
    def __init__(self, total=None,  metrics_key_format=None):
        self._total = total
        self._key = metrics_key_format

    @property
    def key(self):
        return self._key

    def increment(self, count=1):
        """ Increments the counter and returns the result"""
        r = get_redis_connection()
        return r.incr(self._key, count)

    def decrement(self, count=1):
        """ Decrements the counter and returns the result"""
        r = get_redis_connection()
        return r.decr(self._key, count)

    def count(self):
        r = get_redis_connection()
        try:
            return int(r.get(self.key))
        except TypeError:
            return 0

    # Easyer for counter time metrics
    @classmethod
    def get_count(cls, key):
        r = get_redis_connection()
        try:
            return int(r.get(key))
        except TypeError:
            return 0


class CounterTimeMetrics(CounterMetrics):
    """ Abstract Counter Metrics  in time """

    def __init__(self, metrics_date=None, total=None,  metrics_key_format=None,
                 date_format=None):
        super(CounterTimeMetrics, self).__init__(total=total)

        self._METRICS_KEY = metrics_key_format
        self._DATE_FORMAT = date_format  # Use Standard ISO-8601

        if not metrics_date:
            metrics_date = datetime_now_utc()
        self._metrics_date = metrics_date

        time = self._metrics_date.strftime(self._DATE_FORMAT)
        key = self._METRICS_KEY.format(time)

        self._key = key

    @property
    def metrics_date(self):
        return self._metrics_date

    @metrics_date.setter
    def metrics_date(self, value):
        self.metrics_date = value
        time = self.metrics_date.strftime(self._DATE_FORMAT)
        self._key = self._METRICS_KEY.format(time)

    def total_counts_per_hours(self):
        """ Returns a list from 0 to 23 with the counts for each hour"""

        results = []

        for i in range(24):
            date = datetime(year=self.metrics_date.year,
                            month=self.metrics_date.month,
                            day=self.metrics_date.day,
                            hour=i).strftime(self._DATE_FORMAT)
            key = self._METRICS_KEY.format(date)

            results.append(CounterMetrics.get_count(key))

        return results

    def total_counts_per_day(self):
        """ Returns the count of the day"""
        return sum(self.total_counts_per_hours())


class SharedLinkMetrics(CounterTimeMetrics):

    def __init__(self,
                 metrics_date=None,
                 total=None,
                 metrics_key_format="Metrics:sharedlinks:{0}",
                 date_format="%Y-%m-%dT%H"):
        super(SharedLinkMetrics, self).__init__(metrics_date=metrics_date,
                                                 total=total,
                                                 metrics_key_format=metrics_key_format,
                                                 date_format=date_format)

    def count_hours_shared_links(self):
        return self.total_counts_per_hours()


class ClickMetrics(CounterTimeMetrics):

    def __init__(self,
                 metrics_date=None,
                 total=None,
                 metrics_key_format="Metrics:clicks:{0}",
                 date_format="%Y-%m-%dT%H"):
        super(ClickMetrics, self).__init__(metrics_date=metrics_date,
                                                 total=total,
                                                 metrics_key_format=metrics_key_format,
                                                 date_format=date_format)

    def count_hours_clicks(self):
        return self.total_counts_per_hours()

class TotalClickMetrics(CounterMetrics):
    def __init__(self,
                 total=None,
                 metrics_key_format="Metrics:totalclicks:{0}"):
        super(TotalClickMetrics, self).__init__(total=total,
                                    metrics_key_format=metrics_key_format)
