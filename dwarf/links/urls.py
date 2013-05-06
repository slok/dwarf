from django.conf.urls import patterns, url

import links.views


urlpatterns = patterns('',

    url(r'^$', links.views.links_index, name="links-index"),
    url(r'^info/(?P<token>\w+)$', links.views.links_info, name="links-info"),
)
