from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.core.exceptions import ObjectDoesNotExist

from dwarfutils.hashutils import get_random_hash
from level.models import Level


class Profile(models.Model):
    user = models.OneToOneField(User)
    url = models.CharField(max_length=50)
    points = models.PositiveIntegerField(default=0)
    level = models.ForeignKey(Level, null=True)

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


def user_post_save(sender, instance, created, **kwargs):
    """Create a user profile when a new user account is created"""
    if created:
        p = Profile()
        p.user = instance
        p.activation_token = get_random_hash()

        # set the level to 0s (For the first user when syncdb catch exception)
        try:
            p.level = Level.objects.get(level_number=0)
        except ObjectDoesNotExist:
            pass

        p.save()

post_save.connect(user_post_save, sender=User)
