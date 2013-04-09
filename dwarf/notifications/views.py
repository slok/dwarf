import math

from django.shortcuts import (render_to_response,
                              RequestContext)
from django.http import Http404
from django.contrib.auth.decorators import login_required

from notifications.models import Notification

NOTIFICATIONS_PER_PAGE = 10


@login_required
def notifications_index(request):
    # get the page
    page = int(request.GET.get('page', 1))

    # Get the total pages (rounding up, ex: 1.2 pages means 2 pages)
    total_pages = int(math.ceil(float(Notification.count(request.user)) / NOTIFICATIONS_PER_PAGE))

    # If the page doesn't exists then 404
    if page > total_pages and total_pages > 0:
        raise Http404

    # Get the notifications
    offset = NOTIFICATIONS_PER_PAGE * (page - 1)
    limit = offset + NOTIFICATIONS_PER_PAGE
    notifications = Notification.find(request.user, offset, limit-1)

    context = {
        "total_pages": total_pages,
        "actual_page": page,
        "notifications": notifications
    }

    return render_to_response('notifications/notifications-index.html',
                              context,
                              context_instance=RequestContext(request))
