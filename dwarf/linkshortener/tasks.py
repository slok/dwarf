from celery import task
from django.contrib.auth.models import User

from linkshortener.models import ShortLink, UserLink
from dwarfutils.urlutils import extract_url_title


@task()
def create_token(url, user_id=None):
    # Get the next counter to create the token
    counter = ShortLink.incr_counter()

    # Get the title
    # Fix this!! test if the url exists or not!!
    try:
        title = extract_url_title(url)
    except:
        title = "No title"

    # Create the instance with the data
    sl = ShortLink()
    sl.counter = counter
    sl.url = url
    sl.title = title

    # Save
    sl.save()

    # If is a user link save it also
    if user_id:
        user_link = UserLink()
        user_link.user = User.objects.get(id=user_id)
        user_link.token = sl.token
        user_link.save()

    # Return the new token
    return sl.token
