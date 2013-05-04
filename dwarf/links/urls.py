from django.conf.urls import patterns, url

import links.views


urlpatterns = patterns('',

    url(r'^$', links.views.links_index, name="links-index"),
)
