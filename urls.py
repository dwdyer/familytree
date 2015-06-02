from django.conf.urls import patterns, include, url
from django.contrib import admin
import os.path
import settings

urlpatterns = patterns('',
    (r'^people/', include('people.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^tinymce/', include('tinymce.urls')),
)

# Get Django to serve media files in debug mode.
if settings.DEBUG:
    urlpatterns += patterns('', (r'^resources/(?P<path>.*)$',
                                 'django.views.static.serve',
                                 {'document_root': settings.MEDIA_ROOT}))
