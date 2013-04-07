import random

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from achievements.models import Achievement
from achievements.signals.receivers import save_achievement


class Command(BaseCommand):
    args = '<user_id achievement_id>'
    help = 'Adds an achievement to the user'

    def handle(self, *args, **options):
        user = User.objects.get(id=int(args[0]))
        achiv = Achievement.objects.get(id=args[1])

        save_achievement(user, achiv)
