from django.conf.urls import patterns, url

import simple.views

urlpatterns = patterns('',
    url(r'details/(?P<token>\w+)$', simple.views.details, name="simple-link-details"),
    url(r'$', simple.views.index, name="simple-index"),
)
