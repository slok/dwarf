import re

from django.shortcuts import redirect

from linkshortener.models import ShortLink
from clickmanager.tasks import click_link
from forwarder import settings
from level import utils
from linkshortener.models import UserLink


def forward(request, token):

    # Click :)
    click_link(token, request.META)

    # get the forwarding Forward
    sl = ShortLink.find(token=token)
    if not re.search("^https?://.+", sl.url):
        forward_url = "http://{0}".format(sl.url)
    else:
        forward_url = sl.url

    # Add the points to the user
    user_link = UserLink.objects.get(token=token)
    # If returns something then level upload then notification
    if utils.incr_points(user_link.user, settings.POINTS_PER_CLICK):
        #TODO send notification
        pass

    return redirect(forward_url)
