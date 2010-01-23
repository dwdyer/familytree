from django.conf.urls.defaults import *

urlpatterns = patterns('familytree.people.views',
    (r'^(?P<person_id>\d+)/$', 'person'),
)

