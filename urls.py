from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import RedirectView
import os.path
import settings

urlpatterns = patterns(
    '',
    (r'^$', RedirectView.as_view(pattern_name='people.index', permanent=False)),
    (r'^people/', include('people.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^tinymce/', include('tinymce.urls')),
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/login/'}, name='logout'),  
)

# Get Django to serve media files in debug mode.
if settings.DEBUG:
    urlpatterns += patterns('', (r'^media/(?P<path>.*)$',
                                 'django.views.static.serve',
                                 {'document_root': settings.MEDIA_ROOT}))
