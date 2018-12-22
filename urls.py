from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import RedirectView
import django.views.static
import os.path
import settings

urlpatterns = [
    url(r'', include('people.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^login/$', LoginView.as_view(template_name='login.html'), name='login'),
    url(r'^logout/$', LogoutView.as_view(next_page='/'), name='logout'),
]

# Get Django to serve media files in debug mode.
if settings.DEBUG:
    urlpatterns += [url(r'^media/(?P<path>.*)$',
                        django.views.static.serve,
                        {'document_root': settings.MEDIA_ROOT})]
