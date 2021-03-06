import logging

from django.shortcuts import (render_to_response,
                             RequestContext, redirect)
from django.http import HttpResponse, Http404
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from achievements.models import Achievement, UserAchievement
from achievements.signals.signals import user_signup
from metrics.models import AchievementMetrics

logger = logging.getLogger("dwarf")


@login_required
def list_achievements(request):

    # Global achievements
    achievements_tmp = Achievement.objects.all()
    users = User.objects.all().count()
    achievements = []

    # Login required page, not needed to check
    user = request.user

    for i in achievements_tmp:
        metrics = AchievementMetrics(i.id)
        total = metrics.total_users()
        try:
            percent = total * 100 / users
        except ZeroDivisionError:
            percent = 0

        own = metrics.user_has_achievement(user.id) == 1
        achievements.append((i, percent, own))

    # User achievements
    total_achievements_len = len(achievements_tmp)
    user_achievements_len = UserAchievement.objects.filter(user=user).count()
    try:
        user_percent = 100 * user_achievements_len / total_achievements_len
    except ZeroDivisionError:
        user_percent = 0

    context = {
        'achievements': achievements,
        'user_metrics': (total_achievements_len,
                         user_achievements_len,
                         user_percent)
    }

    return render_to_response('achievements/achievements.html',
                              context,
                              context_instance=RequestContext(request))
