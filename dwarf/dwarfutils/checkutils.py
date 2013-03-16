import re

# Only contains alphanumeric characters or dashes and cannot begin with a dash
USERNAME_REGEX = "^[a-zA-Z\d][a-zA-Z\d-]*$"


def username_correct(user):
    return True if re.search(USERNAME_REGEX, user) else False
