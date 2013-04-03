import logging

from metrics.models import AchievementMetrics
from achievements import achievementsids
from achievements.models import Achievement, UserAchievement


logger = logging.getLogger("dwarf")


def save_achievement(user, achievement):
    """ Shortcut to save an achievement"""
    # Save user achievement
    user_achiv = UserAchievement()
    user_achiv.achievement = achievement
    user_achiv.user = user
    user_achiv.save()

    # Save metrics
    metrics = AchievementMetrics(achievementsids.PADAWAN)
    metrics.add_user_achievement(user.id)

    logger.debug("{0} gained '{1}'".format(user.username, achievement.name))


def padawan_achievement(sender, **kwargs):
    achiv = Achievement.objects.get(id=achievementsids.PADAWAN)
    save_achievement(sender, achiv)


def login_achievement(sender, **kwargs):
    print("Login achievement gained! {0}".format(sender.username))
