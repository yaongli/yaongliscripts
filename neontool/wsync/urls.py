import os
from django.utils.translation import ugettext_lazy as _
from django.conf.urls.defaults import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = patterns('',
    url(r'^$', 'wsync.views.home', name='wsync'),
)
