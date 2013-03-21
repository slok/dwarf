from django.shortcuts import (render_to_response, RequestContext)

from statistics.models import LoginStatistics


def day_logins(request):

    context = {
        "data": LoginStatistics().count_hours_logins(),
    }

    return render_to_response('statistics/daylogins.html',
                              context,
                              context_instance=RequestContext(request))
