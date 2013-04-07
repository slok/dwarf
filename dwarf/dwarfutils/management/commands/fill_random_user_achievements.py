import random

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from achievements.models import Achievement
from achievements.signals.receivers import save_achievement


class Command(BaseCommand):
    help = 'Fills random achievements for all the users'

    def handle(self, *args, **options):
        users = User.objects.all()
        # Dont use count, we are going to use later
        achievements = Achievement.objects.all()
        a_length = len(achievements)

        # For every user
        for user in users:
            # How many achievements?
            user_achiev = set([random.randrange(1, a_length+1) for i in range(a_length)])
            for achiev in user_achiev:
                a = Achievement.objects.get(id=achiev)
                save_achievement(user, a)
