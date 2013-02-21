from django.conf.urls import patterns, url

import userprofile.views


urlpatterns = patterns('',

    url(r'^activate/(?P<user_id>\d+)/(?P<token>\w{64})/',
        userprofile.views.activate_account, name="userprofile-activate"),
)
