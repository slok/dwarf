import logging

from metrics.models import AchievementMetrics
from achievements import achievementsids
from achievements.models import Achievement, UserAchievement


logger = logging.getLogger("dwarf")


def padawan_achievement(sender, **kwargs):
    achiv = Achievement.objects.get(id=achievementsids.PADAWAN)

    # Save user achievement
    user_achiv = UserAchievement()
    user_achiv.achievement = achiv
    user_achiv.user = sender
    user_achiv.save()

    # Save metrics
    metrics = AchievementMetrics(achievementsids.PADAWAN)
    metrics.add_user_achievement(sender.id)

    logger.debug("Padawan achievement gained! {0}".format(sender.username))


def login_achievement(sender, **kwargs):
    print("Login achievement gained! {0}".format(sender.username))
