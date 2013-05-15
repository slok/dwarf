import re

from django.shortcuts import redirect
from django.http import Http404

from linkshortener.models import ShortLink
from clickmanager.tasks import click_link
from forwarder import settings
from level import utils
from linkshortener.models import UserLink
from notifications.models import LevelNotification


def forward(request, token):

    # get the forwarding Forward
    sl = ShortLink.find(token=token)

    if sl.disabled:
        raise Http404

    # Click :)
    click_link(token, request.META)

    if not re.search("^https?://.+", sl.url):
        forward_url = "http://{0}".format(sl.url)
    else:
        forward_url = sl.url

    # Add the points to the user
    user_link = UserLink.objects.get(token=token)
    # If returns something then level upload then notification
    new_level = utils.incr_points(user_link.user, settings.POINTS_PER_CLICK)
    if new_level:
        # Send notifications
        notif = LevelNotification(level=new_level,
                                  user_id=user_link.user.id)
        #notif.send_push()  # Push realtime notification
        notif.save()  # save the notification for the dashboard

    return redirect(forward_url)
