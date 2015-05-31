from django.conf.urls import patterns

urlpatterns = patterns('people.views',
    (r'^(?P<person_id>\d+)/$', 'person'),
    (r'^(?P<person_id>\d+)/relatives/$', 'relatives'),
    (r'^(?P<person_id>\d+)/relatives/descendants/$', 'descendants'),
    (r'^(?P<person_id>\d+)/relatives/ancestors/$', 'ancestors'),
)

