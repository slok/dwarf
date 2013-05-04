import logging
import math

from django.shortcuts import render_to_response, RequestContext
from django.http import Http404
from django.contrib.auth.decorators import login_required

from linkshortener.models import UserLink, ShortLink
from dwarfutils.dateutils import unix_to_datetime


logger = logging.getLogger("dwarf")

LINK_PER_PAGE = 10


@login_required
def links_index(request):

    # get the page
    page = int(request.GET.get('page', 1))

    # Get the total pages (rounding up, ex: 1.2 pages means 2 pages)
    total_pages = int(math.ceil(
                        float(UserLink.objects.filter(
                                user=request.user).count()) / LINK_PER_PAGE))

    # If the page doesn't exists then 404
    if page > total_pages and total_pages > 0:
        raise Http404

    # Get the links
    offset = LINK_PER_PAGE * (page - 1)
    limit = offset + LINK_PER_PAGE
    links_aux = UserLink.objects.filter(user=request.user).order_by('-id')[offset:limit]
    links = [ShortLink.find(token=i.token) for i in links_aux]

    # Group by day
    grouped_links = []
    temp = []

    for i in links:
        creation_date = unix_to_datetime(i.creation_date)

        if len(temp) == 0:
            temp.append(i)
        else:
            previous_date = unix_to_datetime(temp[0].creation_date)
            if previous_date.year == creation_date.year and\
                    previous_date.month == creation_date.month and\
                    previous_date.day == creation_date.day:
                temp.append(i)
            else:
                grouped_links.append(temp)
                temp = []
    # If no links don't add them
    if temp:
        grouped_links.append(temp)

    context = {
        "total_pages": total_pages,
        "actual_page": page,
        "links": grouped_links
    }

    return render_to_response('userprofile/dashboard.html',
                              context,
                              context_instance=RequestContext(request))
