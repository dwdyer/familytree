from django.conf.urls import patterns, include, url
from django.contrib import admin
import os.path

urlpatterns = patterns('',
    (r'^people/', include('people.urls')),

    (r'^admin/', include(admin.site.urls)),
    (r'^media/templates/(?P<path>.*)$',
     'django.views.static.serve',
     {'document_root': os.path.join(os.path.dirname(__file__), 'templates/media').replace('\\','/')}),
    (r'^media/(?P<path>.*)$',
     'django.views.static.serve',
     {'document_root': os.path.join(os.path.dirname(__file__), 'media').replace('\\','/')}),
)
