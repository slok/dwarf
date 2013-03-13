from django.conf.urls import patterns, url
from django.contrib.auth.views import logout

import userprofile.views


urlpatterns = patterns('',

     url(r'^$',
        userprofile.views.user_dashboard, name="userprofile-dashboard"),

    # Sign up stuff
    url(r'^activate/(?P<user_id>\d+)/(?P<token>\w{64})/$',
        userprofile.views.activate_account, name="userprofile-activate"),

    url(r'^signup/$', userprofile.views.signup, name="userprofile-signup"),

    # Login stuff
    url(r'^login/$', userprofile.views.custom_login,
        {'template_name': 'userprofile/login.html'},
        name="userprofile-login"),

    url(r'^logout/$', logout, {'next_page': '/'},
         name="userprofile-logout"),

    # Password reset stuff
    url(r'^ask/reset/password/$',
        userprofile.views.ask_reset_password,
        name="userprofile-ask-reset-password"),

    url(r'^reset/password/(?P<user_id>\d+)/(?P<token>\w{64})/$',
        userprofile.views.reset_password,
        name="userprofile-reset-password"),
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
