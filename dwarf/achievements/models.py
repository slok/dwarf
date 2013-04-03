from django.db import models
from django.contrib.auth.models import User

from dwarfutils.models import AutoDateTimeField


class Achievement(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=1000)
    image = models.CharField(max_length=100)
    points = models.IntegerField()
    level = models.IntegerField()
    secret = models.BooleanField(default=False)

    def __unicode__(self):
        return u"{0}".format(self.name)


# I dont want to use defer for lazy loading, so we split the model in
# a new table(https://docs.djangoproject.com/en/dev/ref/models/querysets/#defer)
class UserAchievement(models.Model):
    achievement = models.ForeignKey(Achievement)
    user = models.ForeignKey(User)
    date = AutoDateTimeField()

    # Simulate multiple primary key (Django doesn't support) restriction
    class Meta:
        unique_together = (("user", "achievement"),)

    def __unicode__(self):
        return "{0} of user {1}".format(
                                self.achievement.name, self.user.username)


# register all the signals
import achievements.signals.register
