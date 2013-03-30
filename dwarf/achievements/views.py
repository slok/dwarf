import logging

from django.shortcuts import (render_to_response,
                             RequestContext, redirect)
from django.http import HttpResponse, Http404
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from achievements.models import Achievement

logger = logging.getLogger("dwarf")


@login_required
def list_achievements(request):
    achievements = Achievement.objects.all()
    context = {
        'achievements': achievements,
    }

    return render_to_response('achievements/achievements.html',
                              context,
                              context_instance=RequestContext(request))
