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
        self.r.flushdb()

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

    def test_and_operation(self):
        and_bitmaps = {
            "test:andops:1": (1, 1, 0, 1, 0, 0, 0, 0, 1, 1),
            "test:andops:2": (1, 0, 0, 1, 1, 0, 1, 0, 1, 1),
            "test:andops:3": (1, 0, 0, 1, 0, 0, 0, 0, 1, 1),
            "test:andops:4": (1, 1, 0, 1, 0, 0, 0, 0, 0, 1),
        }

        result = (1, 0, 0, 1, 0, 0, 0, 0, 0, 1)

        # Initial State
        for key, val in and_bitmaps.items():
            for i in range(len(val)):
                self.r.setbit(key, i, val[i])

        # After login
        store_key_default = "test:andops:result"
        store_key = LoginStatistics.and_operation(and_bitmaps.keys(),
                                                  store_key_default)

        #Check if the store key is the same
        self.assertEquals(store_key_default, store_key)

        for i in range(len(result)):
            self.assertEquals(result[i], self.r.getbit(store_key, i))

    def test_and_operation_random_result_key(self):
        and_bitmaps = {
            "test:andops:1": (1, 1, 0, 1, 0, 0, 0, 0, 1, 1),
            "test:andops:2": (1, 0, 0, 1, 1, 0, 1, 0, 1, 1),
            "test:andops:3": (1, 0, 0, 1, 0, 0, 0, 0, 1, 1),
            "test:andops:4": (1, 1, 0, 1, 0, 0, 0, 0, 0, 1),
        }

        result = (1, 0, 0, 1, 0, 0, 0, 0, 0, 1)

        # Initial State
        for key, val in and_bitmaps.items():
            for i in range(len(val)):
                self.r.setbit(key, i, val[i])

        # After login
        store_key = LoginStatistics.and_operation(and_bitmaps.keys())

        for i in range(len(result)):
            self.assertEquals(result[i], self.r.getbit(store_key, i))

    def test_or_operation(self):
        or_bitmaps = {
            "test:orops:1": (1, 1, 0, 1, 0, 0, 0, 0, 1, 1),
            "test:orops:2": (1, 0, 0, 1, 1, 0, 1, 0, 1, 1),
            "test:orops:3": (1, 0, 0, 1, 0, 0, 0, 0, 1, 1),
            "test:orops:4": (1, 1, 0, 1, 0, 0, 0, 0, 0, 1),
        }

        result = (1, 1, 0, 1, 1, 0, 1, 0, 1, 1)

        # Initial State
        for key, val in or_bitmaps.items():
            for i in range(len(val)):
                self.r.setbit(key, i, val[i])

        # After login
        store_key_default = "test:orops:result"
        store_key = LoginStatistics.or_operation(or_bitmaps.keys(),
                                                 store_key_default)

        #Check if the store key is the same
        self.assertEquals(store_key_default, store_key)

        for i in range(len(result)):
            self.assertEquals(result[i], self.r.getbit(store_key, i))

    def test_xor_operation(self):
        xor_bitmaps = {
            "test:xorops:1": (1, 1, 0, 1, 0, 0, 0, 0, 1, 1),
            "test:xorops:2": (1, 0, 0, 1, 1, 0, 1, 0, 1, 1),
            "test:xorops:3": (1, 0, 0, 1, 0, 0, 0, 0, 1, 1),
            "test:xorops:4": (1, 1, 0, 1, 0, 0, 0, 0, 0, 1),
        }

        result = (0, 0, 0, 0, 1, 0, 1, 0, 1, 0)

        # Initial State
        for key, val in xor_bitmaps.items():
            for i in range(len(val)):
                self.r.setbit(key, i, val[i])

        # After login
        store_key_default = "test:xorops:result"
        store_key = LoginStatistics.xor_operation(xor_bitmaps.keys(),
                                                  store_key_default)

        #Check if the store key is the same
        self.assertEquals(store_key_default, store_key)

        for i in range(len(result)):
            self.assertEquals(result[i], self.r.getbit(store_key, i))

    def test_not_bitmap(self):

        bitmaps = (
            ((1, 1, 0, 1, 0, 0, 0, 0, 1, 1), (0, 0, 1, 0, 1, 1, 1, 1, 0, 0)),
            ((1, 0, 0, 1, 1, 0, 1, 0, 1, 1), (0, 1, 1, 0, 0, 1, 0, 1, 0, 0)),
            ((1, 0, 0, 1, 0, 0, 0, 0, 1, 1), (0, 1, 1, 0, 1, 1, 1, 1, 0, 0)),
            ((1, 1, 0, 1, 0, 0, 0, 0, 0, 1), (0, 0, 1, 0, 1, 1, 1, 1, 1, 0)),
            ((0, 0, 0, 0, 0, 0, 0, 0, 0, 0), (1, 1, 1, 1, 1, 1, 1, 1, 1, 1)),
        )

        for bitmap_result in bitmaps:
            bitmap = bitmap_result[0]
            key = "test:{0}:result".format(random.randrange(0, 100000))
            result = bitmap_result[1]

            for i in range(len(bitmap)):
                self.r.setbit(key, i, bitmap[i])

            # Apply NOT
            result_key = LoginStatistics.not_operation(key)

            # Check
            for i in range(len(result)):
                self.assertEquals(result[i], self.r.getbit(result_key, i))

    def test_get_bit_from_bitmap(self):

        bitmap = (1, 1, 0, 1, 0, 0, 0, 0, 1, 1)
        key = "test:get:result"

        for i in range(len(bitmap)):
            self.r.setbit(key, i, bitmap[i])

        for i in range(len(bitmap)):
            self.assertEquals(bitmap[i], LoginStatistics.check_flag(key, i))

    def test_count_bitmap(self):

        bitmaps = (
            ((1, 1, 0, 1, 0, 0, 0, 0, 1, 1), 5),
            ((1, 0, 0, 1, 1, 0, 1, 0, 1, 1), 6),
            ((1, 0, 0, 1, 0, 0, 0, 0, 1, 1), 4),
            ((1, 1, 0, 1, 0, 0, 0, 0, 0, 1), 4),
            ((0, 0, 0, 0, 0, 0, 0, 0, 0, 0), 0),
        )

        for bitmap_result in bitmaps:
            bitmap = bitmap_result[0]
            key = "test:{0}:result".format(random.randrange(0, 100000))
            good_result = bitmap_result[1]

            for i in range(len(bitmap)):
                self.r.setbit(key, i, bitmap[i])

            self.assertEquals(good_result, LoginStatistics.count_flags(key))
