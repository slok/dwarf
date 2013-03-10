from django.conf.urls import patterns, url

import linkshortener.views


urlpatterns = patterns('',

    url(r'^createlink/$',
        linkshortener.views.create_link, name="linkshortener-createlink"),
)