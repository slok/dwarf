from django.conf.urls import patterns, url
from django.contrib.auth.views import logout

import userprofile.views


urlpatterns = patterns('',

    # Sign up stuff
    url(r'^activate/(?P<user_id>\d+)/(?P<token>\w{64})/$',
        userprofile.views.activate_account, name="userprofile-activate"),

    url(r'^signup/$', userprofile.views.signup, name="userprofile-signup"),

    # Login stuff
    url(r'^login/$', userprofile.views.custom_login,
        {'template_name': 'userprofile/login.html'},
        name="userprofile-login"),

    url(r'^logout/$', logout, name="userprofile-logout"),

    # Password reset stuff
)

ajax_patterns = patterns('',
    url(r'^signup/userexists/(?P<username>\w+)/$',
        userprofile.views.ajax_username_exists,
        name="userprofile-ajax-userexists"),
    url(r'^signup/emailexists/$',
        userprofile.views.ajax_email_exists,
        name="userprofile-email-userexists"),
)

urlpatterns += ajax_patterns
