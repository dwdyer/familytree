from django.conf.urls.defaults import *

urlpatterns = patterns('familytree.people.views',
    (r'^(?P<person_id>\d+)/$', 'person'),
    (r'^(?P<person_id>\d+)/relatives/$', 'relatives'),
    (r'^(?P<person_id>\d+)/relatives/descendants/$', 'descendants'),
    (r'^(?P<person_id>\d+)/relatives/ancestors/$', 'ancestors'),
)

