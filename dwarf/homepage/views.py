from django.shortcuts import (render_to_response,
                             RequestContext, redirect)

from django.contrib.auth.models import User

from linkshortener.models import ShortLink
from metrics.models import TotalClickMetrics


def index(request):

    context = {
        'total_users': User.objects.all().count(),
        'total_links': ShortLink.get_counter(),
        'total_clicks': TotalClickMetrics().count()

    }

    return render_to_response('homepage/index.html',
                            context,
                            context_instance=RequestContext(request))
