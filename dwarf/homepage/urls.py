from django.conf.urls import patterns, url

import homepage.views


urlpatterns = patterns('',

    url(r'^$', homepage.views.index, name="homepage-index"),
)
