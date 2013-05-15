from django.conf.urls import patterns, url

import links.views


urlpatterns = patterns('',

    url(r'^$', links.views.links_index, name="links-index"),
    url(r'^info/(?P<token>\w+)$', links.views.links_info, name="links-info"),
    url(r'^disable/$', links.views.disable_link, name="links-disable"),
    url(r'^delete/$', links.views.delete_link, name="links-delete"),
)
