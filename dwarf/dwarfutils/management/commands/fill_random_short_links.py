import random

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from linkshortener.tasks import create_token


URLS = (
    "http://www.google.com",
    "http://www.github.com",
    "http://www.python.org",
    "http://mail.google.com",
    "http://www.pogdesign.co.uk/cat/graph/",
    "https://speakerdeck.com/slok",
    "https://github.com/slok/dwarf",
    "http://127.0.0.1:8000/notifications/",
    "http://twitter.github.io/bootstrap/components.html#labels-badges",
    "http://www.humblebundle.com/",
    "https://twitter.com/sLoK69",
    "http://grooveshark.com/#!/artist/Amon+Amarth/17733",
    "https://news.ycombinator.com/",
    "http://highscalability.com/",
    "https://coderwall.com/slok",
    "https://docs.djangoproject.com/en/1.5/topics/db/managers/",
    "http://flask.pocoo.org/",
    "http://pygments.org/faq/#how-to-use",
    "http://docs.vagrantup.com/v2/getting-started/up.html",
    "http://ansible.cc/docs/patterns.html",
)


class Command(BaseCommand):
    help = 'Fills random urls for all the users'

    def handle(self, *args, **options):
        users = User.objects.all()

        # For every user
        for user in users:
            # How many ruls?
            urls = set([URLS[random.randrange(0, len(URLS))] for i in range(random.randrange(0, len(URLS)))])
            for url in urls:
                print(url)
                print(create_token(url, user.id))

