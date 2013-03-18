from dwarfutils.redisutils import get_redis_connection


class BitmapStatistics(object):
    """ This class is an abstract class that represents a redis bitmap for
    statistics.

    The statistics are based on 1 and 0 values along a bitmap, each position
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

    def __init__(self, bitmap=None):
        self._bitmap = bitmap
        self._key = None

    @property
    def key(self):
        return self._key

    def set_flag(self, flag_position):
        r = get_redis_connection()
        r.setbit(self._key, flag_position, BitmapStatistics.FLAG_UP)

    def unset_flag(self, flag_position):
        r = get_redis_connection()
        r.setbit(self._key, flag_position, BitmapStatistics.FLAG_DOWN)

    def set_flags(self, flag_positions):
        r = get_redis_connection()
        pipe = r.pipeline()
        for i in flag_positions:
            pipe.setbit(self._key, i, BitmapStatistics.FLAG_UP)
        pipe.execute()

    def unset_flags(self, flag_positions):
        r = get_redis_connection()
        pipe = r.pipeline()
        for i in flag_positions:
            pipe.setbit(self._key, i, BitmapStatistics.FLAG_DOWN)
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


class LoginStatistics(BitmapStatistics):
    """ Bitmap statistics for  the users that have been logged in a certain
    moment in time.

        * bitmap flag 1 represents that a user has logged in
        * bitmap flag 0 represents that a user hasen't logged yet
        * the position of the bitmap represents the user id
    """

    STATISTICS_KEY = "Statistics:login:{0}"  # Use Standard ISO-8601
    DATE_FORMAT = "%Y-%m-%dT%H:%M"

    def __init__(self, statistics_date=None, bitmap=None):
        super(LoginStatistics, self).__init__(bitmap=bitmap)

        self._statistics_date = statistics_date
        if self._statistics_date:
            time = self._statistics_date.strftime(LoginStatistics.DATE_FORMAT)
            key = LoginStatistics.STATISTICS_KEY.format(time)
        else:
            key = None
        self._key = key

    @property
    def statistics_date(self):
        return self._statistics_date

    @statistics_date.setter
    def statistics_date(self, value):
        self._statistics_date = value
        time = self._statistics_date.strftime(LoginStatistics.DATE_FORMAT)
        self._key = LoginStatistics.STATISTICS_KEY.format(time)
