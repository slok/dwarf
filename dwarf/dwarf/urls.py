from django.conf.urls import patterns, include, url

import simple.urls
import forwarder.urls
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'dwarf.views.home', name='home'),
    url(r'^simple/', include(simple.urls)),
    url(r'^f/', include(forwarder.urls)),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
