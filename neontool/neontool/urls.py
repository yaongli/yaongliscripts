import os
import settings
from django.utils.translation import ugettext_lazy as _
from django.conf.urls.defaults import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'neontool.views.home', name='home'),
    url(r'^signin/$', 'account.views.signin', name='signin'),
    url(r'^signup/$', 'account.views.signup', name='signup'),
    url(r'^change_passwd/$', 'account.views.change_passwd', name='change_passwd'),
    url(r'^signout/$', 'account.views.signout', name='signout'),

    url(r'^wsync/', include('wsync.urls', 'wsync', 'wsync')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

