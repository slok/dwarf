from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

from dwarfutils.hashutils import get_random_hash


class Profile(models.Model):
    user = models.OneToOneField(User)
    url = models.CharField(max_length=50)

    password_reset_token = models.CharField(max_length=64)
    password_reset_token_date = models.DateTimeField(null=True)

    activation_token = models.CharField(max_length=64)
    activated = models.BooleanField(default=False)
    # TODO: Activation time expire

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
        p.activation_token = get_random_hash()
        p.save()

post_save.connect(user_post_save, sender=User)
