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
from achievements.signals.signals import user_signup
from metrics.models import AchievementMetrics

logger = logging.getLogger("dwarf")


@login_required
def list_achievements(request):
    achievements_tmp = Achievement.objects.all()
    users = User.objects.all().count()
    achievements = []

    for i in achievements_tmp:
        total = AchievementMetrics(i.id).total_users()
        percent = total * 100 / users
        achievements.append((i, percent))

    context = {
        'achievements': achievements,
    }

    # Send signal
    #user = User.objects.get(id=1)
    #user_signup.send(sender=user)

    return render_to_response('achievements/achievements.html',
                              context,
                              context_instance=RequestContext(request))
