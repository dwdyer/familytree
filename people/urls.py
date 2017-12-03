from django.conf.urls import url
from people import views

urlpatterns = [
    url(r'^$', views.index, name='people.index'),
    url(r'^person/(?P<person_id>\d+)/$', views.person, name='person'),
    url(r'^person/(?P<person_id>\d+)/edit/$', views.edit_person, name='edit_person'),
    url(r'^person/(?P<person_id>\d+)/relatives/$', views.relatives, name='relatives'),
    url(r'^person/(?P<person_id>\d+)/relatives/map/$', views.relatives_map, name='relatives_map'),
    url(r'^person/(?P<person_id>\d+)/descendants/$', views.descendants, name='descendants'),
    url(r'^person/(?P<person_id>\d+)/descendants/map/$', views.descendants_map, name='descendants_map'),
    url(r'^person/(?P<person_id>\d+)/descendants/tree/$', views.descendants_tree, name='descendants_tree'),
    url(r'^person/(?P<person_id>\d+)/descendants/tree/svg/$', views.descendants_tree_svg, name='descendants_tree_svg'),
    url(r'^person/(?P<person_id>\d+)/ancestors/$', views.ancestors, name='ancestors'),
    url(r'^person/(?P<person_id>\d+)/ancestors/report/$', views.ancestors_report, name='report'),
    url(r'^person/(?P<person_id>\d+)/ancestors/report/undead/$',
        views.ancestors_report_undead,
        name='report_undead'),
    url(r'^person/(?P<person_id>\d+)/ancestors/report/maiden-names/$',
        views.ancestors_report_maiden_names,
        name='report_maiden_names'),
    url(r'^report/alive/(?P<year>\d+)/$', views.alive_in_year, name='alive_in_year'),
    url(r'^person/(?P<person_id>\d+)/ancestors/map/$', views.ancestors_map, name='ancestors_map'),
    url(r'^person/(?P<person_id>\d+)/ancestors/ringchart/$', views.ring_chart, name='ring_chart'),
    url(r'^person/(?P<person_id>\d+)/ancestors/ringchart/svg/$', views.ring_chart_svg, name='ring_chart_svg'),
    url(r'^location/(?P<location_id>\d+)/$', views.location, name='location'),
    url(r'^region/(?P<region_name>[\w\W]+)/$', views.region, name='region'),
    url(r'^surname/(?P<surname>[\w\W]+)/$', views.surname, name='surname'),
    url(r'^forename/(?P<forename>[\w\W]+)/$', views.forename, name='forename'),
    url(r'^tag/(?P<slug>[\w-]+)/$', views.tag, name='tag'),
    url(r'^person/add/$', views.add_person, name='add_person'),
    url(r'^location/add/$', views.add_location, name='add_location'),

    url(r'^public/surnames/$', views.surnames, name='surnames'),
]

