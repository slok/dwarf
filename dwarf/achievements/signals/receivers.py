import logging

from django.db import IntegrityError

from metrics.models import AchievementMetrics
from achievements import achievementsids
from achievements.models import Achievement, UserAchievement
from notifications.models import AchievementNotification


logger = logging.getLogger("dwarf")


def save_achievement(user, achievement):
    """ Shortcut to save an achievement"""
    try:
        # Save user achievement
        user_achiv = UserAchievement()
        user_achiv.achievement = achievement
        user_achiv.user = user
        user_achiv.save()

        # Save metrics
        metrics = AchievementMetrics(achievement.id)
        metrics.add_user_achievement(user.id)

        # Send notifications
        notif = AchievementNotification(achievement, user=user)
        notif.send_push()  # Push realtime notification
        notif.save()  # save the notification for the dashboard

        logger.debug("{0} gained '{1}'".format(user.username, achievement.name))
    except IntegrityError:
        logger.error("{0} already has '{1}'".format(user.username, achievement.name))


def has_achievement(user, achievement):
    return UserAchievement.objects.filter(user=user, achievement=achievement).exists()


def padawan_achievement(sender, **kwargs):
    achiv = Achievement.objects.get(id=achievementsids.PADAWAN)
    save_achievement(sender, achiv)


def login_achievement(sender, **kwargs):
    print("Login achievement gained! {0}".format(sender.username))
