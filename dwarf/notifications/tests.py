"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import time
import json

from django.test import TestCase
from django.contrib.auth.models import User

from achievements.models import Achievement
from notifications.models import (AchievementNotification,
                                  Notification,
                                  ShortLinkNotification,
                                  LevelNotification)
from dwarfutils.redisutils import get_redis_connection
from linkshortener.tasks import create_token
from linkshortener.models import ShortLink
from level.models import Level


class AchievementNotificationTest(TestCase):
    fixtures = ['achievement.json', 'user.json']
    STORE_KEY_FORMAT = "Notifications:{0}"

    def tearDown(self):
        r = get_redis_connection()
        r.flushdb()
#
#    # Cant test because of the redis blocking
#    def test_send_push(self):
#        achieves = Achievement.objects.all()
#        user = User.objects.get(id=1)
#        for i in achieves:
#            notif = AchievementNotification(achievement=i, user=user)
#            notif.send_push()

    def test_achievement_notification_store(self):
        #with three we have enought to test
        achieves = Achievement.objects.all()[:3]
        user = User.objects.get(id=1)

        a_len = len(achieves)

        for i in achieves:
            notif = AchievementNotification(achievement=i, user=user)
            time.sleep(1)
            notif.save()

        r = get_redis_connection()
        res = r.zrange(
            AchievementNotificationTest.STORE_KEY_FORMAT.format(user.id), 0, -1)

        self.assertEquals(a_len, len(res))

        for i in range(len(res)):
            before = achieves[i]
            after = json.loads(res[i])

            self.assertEquals(before.id, after['achievement_id'])

    def test_achievement_notification_get_all_desc(self):
        #with three we have enought to test
        achieves = Achievement.objects.all()[:3]
        user = User.objects.get(id=1)
        r = get_redis_connection()

        a_len = len(achieves)

        for i in achieves:
            notif = AchievementNotification(achievement=i, user=user)
            time.sleep(1)
            key = AchievementNotificationTest.STORE_KEY_FORMAT.format(user.id)
            r.zadd(key, notif.date, notif.to_json())

        # Get notifications
        res = Notification.all(user)[::-1]

        self.assertEquals(a_len, len(res))

        for i in range(len(res)):
            before = achieves[i]
            after = res[i]

            self.assertEquals(before.id, after.achievement_id)

    def test_achievement_notification_get_all_asc(self):
        #with three we have enought to test
        achieves = Achievement.objects.all()[:3]
        user = User.objects.get(id=1)
        r = get_redis_connection()

        a_len = len(achieves)

        for i in achieves:
            notif = AchievementNotification(achievement=i, user=user)
            time.sleep(1)
            key = AchievementNotificationTest.STORE_KEY_FORMAT.format(user.id)
            r.zadd(key, notif.date, notif.to_json())

        # Get notifications
        res = Notification.all(user, desc=False)

        self.assertEquals(a_len, len(res))

        for i in range(len(res)):
            before = achieves[i]
            after = res[i]

            self.assertEquals(before.id, after.achievement_id)

    def test_achievement_notification_find_with_limits(self):
        achieves = Achievement.objects.all()[:5]
        user = User.objects.get(id=1)
        r = get_redis_connection()

        for i in achieves:
            notif = AchievementNotification(achievement=i, user=user)
            time.sleep(1)
            key = AchievementNotificationTest.STORE_KEY_FORMAT.format(user.id)
            r.zadd(key, notif.date, notif.to_json())

        # Get notifications
        res = Notification.find(user, offset=2, limit=3, desc=False)

        achieves = achieves[2:4]  # 2 and 3 only
        a_len = len(achieves)

        self.assertEquals(a_len, len(res))

        for i in range(len(res)):
            before = achieves[i]
            after = res[i]

            self.assertEquals(before.id, after.achievement_id)

    def test_achievement_notification_get_range(self):
        achieves = Achievement.objects.all()[:5]
        notifs = []
        user = User.objects.get(id=1)
        r = get_redis_connection()

        for i in achieves:
            notif = AchievementNotification(achievement=i, user=user)
            time.sleep(1)
            key = AchievementNotificationTest.STORE_KEY_FORMAT.format(user.id)
            r.zadd(key, notif.date, notif.to_json())
            notifs.append(notif)

        achieves = achieves[2:5]  # 2, 3 and 4 only
        a_len = len(achieves)

        # Get notifications
        res = Notification.time_range(user,
                                      lowerbound=notifs[2].date,
                                      upperbound=notifs[4].date,
                                      desc=False)

        self.assertEquals(a_len, len(res))

        for i in range(len(res)):
            before = achieves[i]
            after = res[i]

            self.assertEquals(before.id, after.achievement_id)

    def test_achievement_notification_count(self):
        achieves = Achievement.objects.all()
        user = User.objects.get(id=1)
        r = get_redis_connection()

        for i in achieves:
            notif = AchievementNotification(achievement=i, user=user)
            key = AchievementNotificationTest.STORE_KEY_FORMAT.format(user.id)
            r.zadd(key, notif.date, notif.to_json())

        a_len = len(achieves)

        self.assertEquals(a_len, AchievementNotification.count(user))

    def test_achievement_notification_count_range(self):
        achieves = Achievement.objects.all()[:5]
        notifs = []
        user = User.objects.get(id=1)
        r = get_redis_connection()

        for i in achieves:
            notif = AchievementNotification(achievement=i, user=user)
            time.sleep(1)
            key = AchievementNotificationTest.STORE_KEY_FORMAT.format(user.id)
            r.zadd(key, notif.date, notif.to_json())
            notifs.append(notif)

        achieves = achieves[2:5]  # 2, 3 and 4 only
        a_len = len(achieves)

        lowerbound = notifs[2].date
        upperbound = notifs[4].date

        result = AchievementNotification.count(user, lowerbound, upperbound)
        self.assertEquals(a_len, result)


class ShortLinkNotificationTest(TestCase):
    fixtures = ['user.json']
    STORE_KEY_FORMAT = "Notifications:{0}"

    def setUp(self):
        # Manual fixtures
        urls = ["www.google.com", "github.com", "xlarrakoetxea.org"]
        user = User.objects.get(id=1)
        for i in urls:
            create_token(i, user.id, False)

    def tearDown(self):
        r = get_redis_connection()
        r.flushdb()

    def test_shortlink_notification_store(self):
        #with three we have enought to test
        sls = ShortLink.findall()[:3]
        user = User.objects.get(id=1)

        a_len = len(sls)

        for i in sls:
            notif = ShortLinkNotification(short_link=i, user=user)
            time.sleep(1)  # We need notification order
            notif.save()

        r = get_redis_connection()
        res = r.zrange(
            ShortLinkNotificationTest.STORE_KEY_FORMAT.format(user.id), 0, -1)

        self.assertEquals(a_len, len(res))

        for i in range(len(res)):
            before = sls[i]
            after = json.loads(res[i])

            self.assertEquals(before.token, after['token'])


class LevelNotificationTest(TestCase):
    fixtures = ['user.json', 'level.json']
    STORE_KEY_FORMAT = "Notifications:{0}"

    def tearDown(self):
        r = get_redis_connection()
        r.flushdb()

    def test_level_notification_store(self):
        #with three we have enought to test
        levels = Level.objects.all()[:3]
        user = User.objects.get(id=1)

        a_len = len(levels)

        for i in levels:
            notif = LevelNotification(level=i, user=user)
            time.sleep(1)  # We need notification order
            notif.save()

        r = get_redis_connection()
        res = r.zrange(
            ShortLinkNotificationTest.STORE_KEY_FORMAT.format(user.id), 0, -1)

        self.assertEquals(a_len, len(res))

        for i in range(len(res)):
            before = levels[i]
            after = json.loads(res[i])

            self.assertEquals(before.level_number, after['level'])
