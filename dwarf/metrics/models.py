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
    def and_operation(self, keys, store_key=None):
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
    def or_operation(self, keys, store_key=None):
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
    def xor_operation(self, keys, store_key=None):
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
    def not_operation(self, key, store_key=None):
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
    def check_flag(self, key, position):
        """Checks a bit in the bitmap in the redis databases
        :param key: The key of redis where the bitmap resides
        :param position: The bitmap position to check
        """
        r = get_redis_connection()
        return r.getbit(key, position)

    @classmethod
    def count_flags(self, key):
        """Counts all the flags activated in a given key (containing a bitmap)
        :param key: the key where the bitmap resides
        """
        r = get_redis_connection()
        return r.bitcount(key)


class TimeMetrics(BitmapMetrics):
    """ Bitmap Metrics for  the users that have been logged in a certain
    moment in time.

        * bitmap flag 1 represents that a user has logged in
        * bitmap flag 0 represents that a user hasen't logged yet
        * the position of the bitmap represents the user id
    """

    METRICS_KEY = "Metrics:login:{0}"  # Use Standard ISO-8601
    DATE_FORMAT = "%Y-%m-%dT%H"
    DATE_FORMAT_MINS = "%Y-%m-%dT%H:%M"

    def __init__(self, metrics_date=None, bitmap=None):
        super(TimeMetrics, self).__init__(bitmap=bitmap)

        if not metrics_date:
            metrics_date = datetime_now_utc()
        self._metrics_date = metrics_date
        if self._metrics_date:
            time = self._metrics_date.strftime(TimeMetrics.DATE_FORMAT)
            key = TimeMetrics.METRICS_KEY.format(time)
        else:
            key = None
        self._key = key

    @property
    def metrics_date(self):
        return self._metrics_date

    @metrics_date.setter
    def metrics_date(self, value):
        self.metrics_date = value
        time = self.metrics_date.strftime(TimeMetrics.DATE_FORMAT)
        self._key = TimeMetrics.METRICS_KEY.format(time)

    def total_counts_per_hours(self):
        """ Returns a list from 0 to 23 with the counts for each hour"""

        results = []

        for i in range(24):
            date = datetime(year=self.metrics_date.year,
                            month=self.metrics_date.month,
                            day=self.metrics_date.day,
                            hour=i).strftime(LoginMetrics.DATE_FORMAT)
            key = LoginMetrics.METRICS_KEY.format(date)

            results.append(self.count_flags(key))

        return results


class LoginMetrics(TimeMetrics):

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
