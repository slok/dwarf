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
from notifications.models import AchievementNotification, Notification
from dwarfutils.redisutils import get_redis_connection


class NotificationTest(TestCase):
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
        res = r.zrange(NotificationTest.STORE_KEY_FORMAT.format(user.id), 0, -1)

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
            key = NotificationTest.STORE_KEY_FORMAT.format(user.id)
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
            key = NotificationTest.STORE_KEY_FORMAT.format(user.id)
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
            key = NotificationTest.STORE_KEY_FORMAT.format(user.id)
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
            key = NotificationTest.STORE_KEY_FORMAT.format(user.id)
            r.zadd(key, notif.date, notif.to_json())
            notifs.append(notif)

        achieves = achieves[2:5]  # 2, 4 and 4 only
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
