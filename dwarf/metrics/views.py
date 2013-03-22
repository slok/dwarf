from django.shortcuts import (render_to_response, RequestContext)

from metrics.models import LoginMetrics


def day_logins(request):

    context = {
        "data": LoginMetrics().count_hours_logins(),
    }

    return render_to_response('metrics/daylogins.html',
                              context,
                              context_instance=RequestContext(request))
