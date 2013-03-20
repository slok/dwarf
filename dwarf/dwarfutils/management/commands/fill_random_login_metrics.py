import random
from datetime import datetime

from django.core.management.base import BaseCommand

from statistics.models import LoginStatistics


class Command(BaseCommand):
    args = '<max_users min_users>'
    help = 'Fills login metrics database with random data'

    def handle(self, *args, **options):
        max_users = 5000 if len(args) < 1 else args[0]
        min_users = 0 if len(args) < 2 else args[1]

        # Populate the DB for one day
        for hour in range(24):
            # Create the datetime for the key
            date = datetime(year=2013, month=3, day=20, hour=hour)

            # Get random login users
            logins = range(random.randrange(min_users, max_users))
            users = [random.randrange(min_users, max_users) for i in logins]

            # Save the users
            ls = LoginStatistics(date)
            ls.save_users_login(users)
