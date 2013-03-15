import re

USERNAME_REGEX = "^[\w][\w-]*$"


def username_correct(user):
    return True if re.search(USERNAME_REGEX, user) else False
