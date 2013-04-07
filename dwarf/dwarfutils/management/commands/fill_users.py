from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    args = '<number>'
    help = 'Adds x fake users'

    USERNAME = "user{0}"
    EMAIL = "user{0}@fakemail.com"
    NAME = "User{0}"
    LASTNAME = "Lastname{0}"

    def handle(self, *args, **options):

        for i in range(int(args[0])):
            user = User()
            user.username = Command.USERNAME.format(i)
            user.set_password(user.username)
            user.email = Command.EMAIL.format(i)
            user.first_name = Command.NAME.format(i)
            user.last_name = Command.LASTNAME.format(i)
            user.save()
