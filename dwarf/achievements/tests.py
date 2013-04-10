"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth.models import User

from achievements.models import Achievement, UserAchievement
from achievements.signals import receivers
from achievements import achievementsids
from metrics.models import AchievementMetrics


class AchievementsUtilsTest(TestCase):
    fixtures = ['achievement.json', 'user.json']

    def test_achievement_already_exists(self):
        user = User.objects.get(id=1)
        achievement = Achievement.objects.get(id=1)

        self.assertFalse(receivers.has_achievement(user, achievement))

        UserAchievement(user=user, achievement=achievement).save()

        self.assertTrue(receivers.has_achievement(user, achievement))

    def test_achievement_saver(self):
        user = User.objects.get(id=1)
        achievement = Achievement.objects.get(id=1)

        self.assertFalse(receivers.has_achievement(user, achievement))

        receivers.save_achievement(user, achievement)

        self.assertTrue(receivers.has_achievement(user, achievement))
        #Check in the future also the redis metrics


class AchievementsTest(TestCase):
    def test_padawan_achievement(self):
        user = User()
        user.username = "test"
        user.save()

        achiv = Achievement()
        achiv.name = "padawan test"
        achiv.id = achievementsids.PADAWAN
        achiv.points = 0
        achiv.level = 0
        achiv.save()

        receivers.padawan_achievement(user)

        # Check
        self.assertTrue(UserAchievement.objects.filter(
                                                    user=user,
                                                    achievement=achiv
        ).exists())

        metrics = AchievementMetrics(achievementsids.PADAWAN)
        self.assertTrue(metrics.user_has_achievement(user.id))
