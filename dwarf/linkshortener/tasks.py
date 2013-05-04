from celery import task
from django.contrib.auth.models import User

from linkshortener.models import ShortLink, UserLink
from metrics.models import SharedLinkMetrics
from dwarfutils.urlutils import (extract_url_title,
                                 extract_url_host,
                                 sanitize_url)
from notifications.models import ShortLinkNotification


@task()
def create_token(url, user_id=None):
    # Get the next counter to create the token
    counter = ShortLink.incr_counter()

    # Sanitize the url
    url = sanitize_url(url)

    # Get the title
    # Fix this!! test if the url exists or not!!
    try:
        title = extract_url_title(url)
    except:
        title = "No title"

    # Get the host
    host = extract_url_host(url)

    # Create the instance with the data
    sl = ShortLink()
    sl.counter = counter
    sl.url = url
    sl.title = title
    sl.host = host

    # Save
    sl.save()

    # If is a user link save it also
    if user_id:
        user_link = UserLink()
        user_link.user = User.objects.get(id=user_id)
        user_link.token = sl.token
        user_link.save()

    # Fill the metrics
    SharedLinkMetrics().increment()

    # Send notifications
    notif = ShortLinkNotification(sl, user_id=user_id)
    #notif.send_push()  # Push realtime notification
    notif.save()  # save the notification for the dashboard

    # Return the new token
    return sl.token
