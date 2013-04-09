from django.conf.urls import patterns, url
from django.contrib.auth.views import logout

import notifications.views


urlpatterns = patterns('',
    # Notifications
    url(r'^$',
        notifications.views.notifications_index, name="notifications-index"),
 )
