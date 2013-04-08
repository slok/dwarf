"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth.models import User

from achievements.models import Achievement
from notifications.models import AchievementNotification


#class AchievementNotificationTest(TestCase):
#    fixtures = ['achievement.json', 'user.json']
#
#    # Cant test because of the redis blocking
#    def test_send_push(self):
#        achieves = Achievement.objects.all()
#        user = User.objects.get(id=1)
#        for i in achieves:
#            notif = AchievementNotification(achievement=i, user=user)
#            notif.send_push()
