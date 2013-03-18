import random

from django.test import TestCase
from datetime import datetime


from dwarfutils.redisutils import get_redis_connection
from statistics.models import LoginStatistics


class LoginStatisticsTest(TestCase):
    def setUp(self):
        self.year = 2013
        self.month = "03"
        self.day = 18
        self.hour = 20
        self.minutes = "00"
        self.date = datetime(year=self.year,
                             month=int(self.month),
                             day=self.day,
                             hour=self.hour,
                             minute=int(self.minutes))

        self.r = get_redis_connection()

    def tearDown(self):
        r = get_redis_connection()
        r.flushdb()

    def test_key_generation(self):
        strtime = "{0}-{1}-{2}T{3}:{4}".format(self.year,
                                               self.month,
                                               self.day,
                                               self.hour,
                                               self.minutes)
        good_key = LoginStatistics.STATISTICS_KEY.format(strtime)

        ls = LoginStatistics(self.date)
        self.assertEquals(good_key, ls.key)

    def test_login_user(self):
        user_id = random.randrange(0, 100000)
        ls = LoginStatistics(self.date)

        # Initial State
        bit = self.r.getbit(ls.key, user_id)
        self.assertEquals(LoginStatistics.FLAG_DOWN, bit)

        # After login
        ls.set_flag(user_id)
        bit = self.r.getbit(ls.key, user_id)
        self.assertEquals(LoginStatistics.FLAG_UP, bit)

    def test_login_users(self):
        users_ids = [random.randrange(0, 100000) for i in range(100)]
        ls = LoginStatistics(self.date)

        # Initial State
        for i in users_ids:
            bit = self.r.getbit(ls.key, i)
            self.assertEquals(LoginStatistics.FLAG_DOWN, bit)

        # After login
        ls.set_flags(users_ids)
        for i in users_ids:
            bit = self.r.getbit(ls.key, i)
            self.assertEquals(LoginStatistics.FLAG_UP, bit)

    def test_logout_user(self):
        user_id = random.randrange(0, 100000)
        ls = LoginStatistics(self.date)

        # After login
        ls.set_flag(user_id)
        bit = self.r.getbit(ls.key, user_id)
        self.assertEquals(LoginStatistics.FLAG_UP, bit)

        # after logout State
        ls.unset_flag(user_id)
        bit = self.r.getbit(ls.key, user_id)
        self.assertEquals(LoginStatistics.FLAG_DOWN, bit)

    def test_logout_users(self):
        users_ids = [random.randrange(0, 100000) for i in range(100)]
        ls = LoginStatistics(self.date)

        # After login
        ls.set_flags(users_ids)
        for i in users_ids:
            bit = self.r.getbit(ls.key, i)
            self.assertEquals(LoginStatistics.FLAG_UP, bit)

        # Initial State
        ls.unset_flags(users_ids)
        for i in users_ids:
            bit = self.r.getbit(ls.key, i)
            self.assertEquals(LoginStatistics.FLAG_DOWN, bit)

    def test_user_logged(self):
        user_id = random.randrange(0, 100000)
        ls = LoginStatistics(self.date)

        # Initial State
        self.assertEquals(LoginStatistics.FLAG_DOWN, ls.get_flag(user_id))

        # After login
        ls.set_flag(user_id)
        self.assertEquals(LoginStatistics.FLAG_UP, ls.get_flag(user_id))

    def test_users_logged(self):
        users_ids = [random.randrange(0, 100000) for i in range(100)]
        ls = LoginStatistics(self.date)

        # Initial State
        for i in users_ids:
            self.assertEquals(LoginStatistics.FLAG_DOWN, ls.get_flag(i))

        # After login
        ls.set_flags(users_ids)
        correct_list = [LoginStatistics.FLAG_UP for i in range(len(users_ids))]
        self.assertEquals(correct_list, ls.get_flags(users_ids))

    def test_users_state(self):
        users_ids = [random.randrange(0, 100000) for i in range(100)]
        ls = LoginStatistics(self.date)

        # Initial State
        for i in users_ids:
            self.assertEquals(LoginStatistics.FLAG_DOWN, ls.get_flag(i))

        # After login
        ls.set_flags(users_ids)
        correct_list = [LoginStatistics.FLAG_UP for i in range(len(users_ids))]
        self.assertEquals(correct_list, ls.get_flags(users_ids))

        # take some random users out
        black_ships = [random.randrange(0, len(users_ids)) for i in range(
                                                            len(users_ids))]

        for i in black_ships:
            ls.unset_flag(users_ids[i])
            correct_list[i] = LoginStatistics.FLAG_DOWN

        # Test again
        self.assertEquals(correct_list, ls.get_flags(users_ids))
