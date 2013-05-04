from django.conf.urls import patterns, include, url
from django.contrib import admin

import simple.urls
import forwarder.urls
import homepage.urls
import userprofile.urls
import linkshortener.urls
import metrics.urls
import achievements.urls
import notifications.urls
import links.urls

admin.autodiscover()


urlpatterns = patterns('',

    url(r'^', include(homepage.urls)),
    #TODO: Delete simple app
    url(r'^simple/', include(simple.urls)),
    url(r'^f/', include(forwarder.urls)),
    url(r'^profile/', include(userprofile.urls)),
    url(r'^shortener/', include(linkshortener.urls)),
    url(r'^metrics/', include(metrics.urls)),
    url(r'^achievements/', include(achievements.urls)),
    url(r'^notifications/', include(notifications.urls)),
    url(r'^links/', include(links.urls)),

    url(r'^admin/', include(admin.site.urls)),
)
