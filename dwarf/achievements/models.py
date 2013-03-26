from django.db import models


class Achievement(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=1000)
    points = models.IntegerField()
    level = models.IntegerField()

    def __unicode__(self):
        return u"{0}".format(self.name)
