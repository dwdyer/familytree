from django.conf.urls import url
from people import views

urlpatterns = [
    url(r'^$', views.index, name='people.index'),
    url(r'^(?P<person_id>\d+)/$', views.person, name='person'),
    url(r'^(?P<person_id>\d+)/relatives/$', views.relatives, name='relatives'),
    url(r'^(?P<person_id>\d+)/relatives/map/$', views.relatives_map, name='relatives_map'),
    url(r'^(?P<person_id>\d+)/descendants/$', views.descendants, name='descendants'),
    url(r'^(?P<person_id>\d+)/descendants/map/$', views.descendants_map, name='descendants_map'),
    url(r'^(?P<person_id>\d+)/ancestors/$', views.ancestors, name='ancestors'),
    url(r'^(?P<person_id>\d+)/ancestors/report/$', views.ancestors_report, name='report'),
    url(r'^(?P<person_id>\d+)/ancestors/map/$', views.ancestors_map, name='ancestors_map'),
    url(r'^(?P<person_id>\d+)/ancestors/ringchart/$', views.ring_chart, name='ring_chart'),
    url(r'^(?P<person_id>\d+)/ancestors/ringchart/svg/$', views.ring_chart_svg, name='ring_chart_svg'),
    url(r'^location/(?P<location_id>\d+)/$', views.location, name='location'),
    url(r'^region/(?P<region_name>[\w\W]+)/$', views.region, name='region'),
    url(r'^surname/(?P<surname>[\w\W]+)/$', views.surname, name='surname'),
    url(r'^forename/(?P<forename>[\w\W]+)/$', views.forename, name='forename'),
    url(r'^tag/(?P<slug>[\w-]+)/$', views.tag, name='tag'),
    url(r'^add/$', views.add_person, name='add_person'),
]

