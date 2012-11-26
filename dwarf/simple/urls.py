from django.conf.urls import patterns, url

import simple.views

urlpatterns = patterns('',
     url(r'$', simple.views.index, name="simple-index"),
)
