# coding: utf-8
import os
import settings
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.conf.urls.defaults import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
import urls

urlpatterns = patterns(settings.CONTEXT_PATH,
   url(r'^%s/' % settings.CONTEXT_PATH.strip("/"), include(urls)),
)


