from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save


class Profile(models.Model):
    user = models.OneToOneField(User)
    url = models.CharField(max_length=50)

    def __unicode__(self):
        return u"{0}".format(self.user.username)


class Token(models.Model):
    token = models.CharField(max_length=10)
    user = models.ForeignKey(User)

    def __unicode__(self):
        return u"{0}".format(self.token)


class Achievement(models.Model):
    achievement = models.CharField(max_length=10)
    user = models.ForeignKey(User)

    def __unicode__(self):
        return u"{0}".format(self.achievement)


def user_post_save(sender, instance, created, **kwargs):
    """Create a user profile when a new user account is created"""
    if created == True:
        p = Profile()
        p.user = instance
        p.save()

post_save.connect(user_post_save, sender=User)
