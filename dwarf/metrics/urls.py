from django.conf.urls import patterns, url

import metrics.views


urlpatterns = patterns(
    '',
    url(r'^day/logins$',
    metrics.views.day_logins, name="metrics-day"),
)
