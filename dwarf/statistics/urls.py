from django.conf.urls import patterns, url

import statistics.views


urlpatterns = patterns(
    '',
    url(r'^day/logins$',
    statistics.views.day_logins, name="statistics-day"),
)
