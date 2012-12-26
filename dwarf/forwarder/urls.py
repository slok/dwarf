from django.conf.urls import patterns, url

import forwarder.views

urlpatterns = patterns('',
    url(r'(?P<token>\w+)$',
                forwarder.views.forward,
                name="forwarder-forward"
    ),
)
