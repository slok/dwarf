"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth.models import User

from level import utils
from level.models import Level


class LevelUtilsTest(TestCase):
    fixtures = ['levels.json', 'user.json']

    def test_basic_increment(self):
        incr_points = 50
        user = User.objects.get(id=1)

        self.assertEqual(0, user.profile.points)
        self.assertEqual(0, user.profile.level.level_number)

        level = utils.incr_points(user, incr_points)
        self.assertEqual(incr_points, user.profile.points)
        self.assertEqual(0, user.profile.level.level_number)
        self.assertIsNone(level)

    def test_basic_increment_without_level(self):
        incr_points = 999
        user = User.objects.get(id=1)

        self.assertEqual(0, user.profile.points)
        self.assertEqual(0, user.profile.level.level_number)

        level = utils.incr_points(user, incr_points)
        self.assertEqual(incr_points, user.profile.points)
        self.assertEqual(0, user.profile.level.level_number)
        self.assertIsNone(level)

    def test_basic_increment_with_level(self):
        incr_points = 5000
        user = User.objects.get(id=1)

        self.assertEqual(0, user.profile.points)
        self.assertEqual(0, user.profile.level.level_number)

        level = utils.incr_points(user, incr_points)
        self.assertEqual(incr_points, user.profile.points)
        self.assertEqual(5, user.profile.level.level_number)
        self.assertEqual(5, level.level_number)

    def test_basic_decrement(self):
        decr_points = 50
        user = User.objects.get(id=1)

        self.assertEqual(0, user.profile.points)
        self.assertEqual(0, user.profile.level.level_number)

        level = utils.decr_points(user, decr_points)
        self.assertEqual(0, user.profile.points)
        self.assertEqual(0, user.profile.level.level_number)
        self.assertIsNone(level)

    def test_basic_decrement_without_level(self):
        decr_points = 999
        start_points = 1999

        user = User.objects.get(id=1)
        user.profile.points = start_points
        user.profile.level = Level.objects.get(level_number=1)
        user.save()

        self.assertEqual(start_points, user.profile.points)

        level = utils.decr_points(user, decr_points)
        self.assertEqual(start_points - decr_points, user.profile.points)
        self.assertEqual(1, user.profile.level.level_number)
        self.assertIsNone(level)

    def test_basic_decrement_with_level(self):
        decr_points = 3000
        start_points = 5000

        user = User.objects.get(id=1)
        user.profile.points = start_points
        user.profile.level = Level.objects.get(level_number=5)
        user.save()

        self.assertEqual(start_points, user.profile.points)

        level = utils.decr_points(user, decr_points)
        self.assertEqual(start_points - decr_points, user.profile.points)
        self.assertEqual(2, user.profile.level.level_number)
        self.assertEqual(2, level.level_number)

    def test_remainin_points_for_next_level(self):
        points = 560
        next_level_min = 1000

        user = User.objects.get(id=1)
        user.profile.points = points
        user.save()

        self.assertEqual(next_level_min-points,
                         utils.points_for_next_level(user))
