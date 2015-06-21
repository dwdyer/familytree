from django.conf.urls import patterns, url
from people import views

urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='index'),
    url(r'^(?P<person_id>\d+)/$', views.person, name='person'),
    url(r'^(?P<person_id>\d+)/relatives/$', views.relatives, name='relatives'),
    url(r'^(?P<person_id>\d+)/relatives/descendants/$', views.descendants, name='descendants'),
    url(r'^(?P<person_id>\d+)/relatives/ancestors/$', views.ancestors, name='ancestors'),
    url(r'^(?P<person_id>\d+)/relatives/ancestors/report$', views.ancestors_report, name='report'),
    url(r'^location/(?P<location_id>\d+)/$', views.location, name='location'),
    url(r'^region/(?P<region_name>[\w\W]+)/$', views.region, name='region'),
    url(r'^surname/(?P<surname>[\w\W]+)/$', views.surname, name='surname'),
    url(r'^tag/(?P<slug>[\w-]+)/$', views.tag, name='tag'),
)

