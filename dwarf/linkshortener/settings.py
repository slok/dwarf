from string import ascii_letters, digits

from django.conf import settings


START_URL_TOKEN_LENGTH = getattr(settings, 'START_URL_TOKEN_LENGTH', 4)
ALPHABET = getattr(settings, 'ALPHABET', digits + ascii_letters)
