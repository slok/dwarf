import random
from datetime import datetime

from django.core.management.base import BaseCommand

from metrics.models import LoginMetrics
from dwarfutils.dateutils import datetime_now_utc


class Command(BaseCommand):
    args = '<max_users min_users>'
    help = 'Fills login metrics database with random data'

    def handle(self, *args, **options):
        max_users = 5000 if len(args) < 1 else int(args[0])
        min_users = 0 if len(args) < 2 else int(args[1])
        day = None if len(args) < 3 else int(args[2])

        # Populate the DB for one day
        for hour in range(24):
            # Create the datetime for the key
            now = datetime_now_utc()
            if not day:
                day = now.day
            date = datetime(year=now.year,
                            month=now.month,
                            day=day,
                            hour=hour)

            # Get random login users
            logins = range(random.randrange(min_users, max_users))
            users = [random.randrange(min_users, max_users) for i in logins]

            # Save the users
            ls = LoginMetrics(date)
            ls.save_users_login(users)
