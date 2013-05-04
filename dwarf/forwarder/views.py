import re

from django.shortcuts import redirect

from linkshortener.models import ShortLink
from clickmanager.tasks import click_link


def forward(request, token):

    # Click :)
    click_link(token, request.META)

    # get the forwarding Forward
    sl = ShortLink.find(token=token)
    if not re.search("^https?://.+", sl.url):
        forward_url = "http://{0}".format(sl.url)
    else:
        forward_url = sl.url

    return redirect(forward_url)
