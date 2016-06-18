from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import RedirectView
import django.views.static
import django.contrib.auth.views
import os.path
import settings

urlpatterns = [
    url(r'^$', RedirectView.as_view(pattern_name='people.index', permanent=False)),
    url(r'^people/', include('people.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^login/$', django.contrib.auth.views.login, {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', django.contrib.auth.views.logout, {'next_page': '/login/'}, name='logout'),
]

# Get Django to serve media files in debug mode.
if settings.DEBUG:
    urlpatterns += [url(r'^media/(?P<path>.*)$',
                        django.views.static.serve,
                        {'document_root': settings.MEDIA_ROOT})]
