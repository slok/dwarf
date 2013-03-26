from django.db import models


class Achievement(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=1000)
    image = models.CharField(max_length=100)
    points = models.IntegerField()
    level = models.IntegerField()

    def __unicode__(self):
        return u"{0}".format(self.name)
