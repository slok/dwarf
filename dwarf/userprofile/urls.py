from django.conf.urls import patterns, url

import userprofile.views


urlpatterns = patterns('',

    # Sign up stuff
    url(r'^activate/(?P<user_id>\d+)/(?P<token>\w{64})/$',
        userprofile.views.activate_account, name="userprofile-activate"),

    url(r'^signup/$', userprofile.views.signup, name="userprofile-signup"),

    # Login stuff

    # Password reset stuff
)

ajax_patterns = patterns('',
    url(r'^signup/userexists/(?P<username>\w+)/$',
        userprofile.views.ajax_username_exists,
        name="userprofile-ajax-userexists"),
)

urlpatterns += ajax_patterns
