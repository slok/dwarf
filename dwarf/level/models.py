from django.db import models


class Level(models.Model):
    level_number = models.PositiveIntegerField(default=0, unique=True)
    name = models.CharField(max_length=64, null=True, blank=True)
    points_min = models.PositiveIntegerField(default=0)
    points_max = models.PositiveIntegerField(default=0)
    image = models.CharField(max_length=200, null=True, blank=True)

    def __unicode__(self):
        return u"Level {0} [{1}, {2})".format(self.level_number,
                                              self.points_min,
                                              self.points_max + 1)
