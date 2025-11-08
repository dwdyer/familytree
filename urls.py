from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import include, path, re_path
from django.views.generic import RedirectView
import django.views.static
import os.path
import settings

urlpatterns = [
    path('', include('people.urls')),
    path('admin/', admin.site.urls),
    path('tinymce/', include('tinymce.urls')),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
]

# Get Django to serve media files in debug mode.
if settings.DEBUG:
    urlpatterns += [re_path(r'^media/(?P<path>.*)$',
                            django.views.static.serve,
                            {'document_root': settings.MEDIA_ROOT})]
