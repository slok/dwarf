from django.conf.urls import patterns, url

import achievements.views


urlpatterns = patterns('',

    url(r'^$',
        achievements.views.list_achievements,
        name="achievements-listachievements"),
)
