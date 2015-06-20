from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render
from itertools import groupby
from math import pow
from operator import itemgetter
from people.models import Location, Person

def index(request):
    regions = Location.objects.values('county_state_province',
                                      'country__name',
                                      'country__country_code')
    regions = regions.annotate(Count('natives')).order_by('-natives__count',
                                                          'county_state_province')
    surnames = Person.objects.values('surname').annotate(Count('surname'))
    surnames = surnames.filter(surname__count__gte=2).order_by('surname')

    locations = Location.objects.filter(latitude__isnull=False, longitude__isnull=False)
    min_lat = min_lng = 90
    max_lat = max_lng = -90
    for location in locations:
        min_lat = min(location.latitude, min_lat)
        max_lat = max(location.latitude, max_lat)
        min_lng = min(location.longitude, min_lng)
        max_lng = max(location.longitude, max_lng)
    center = ((min_lat + max_lat) / 2, (min_lng + max_lng) / 2)

    return render(request,
                  'people/index.html',
                  {'surnames': surnames,
                   'regions': regions[:10],
                   'locations': locations,
                   'map_center' : center,
                   'list': Person.objects.all()})


def person(request, person_id):
    person = get_object_or_404(Person, id=person_id)
    return render(request,
                  'people/person.html',
                  {'person': person, 'list': Person.objects.all()})


def relatives(request, person_id):
    person = get_object_or_404(Person, id=person_id)
    title = 'Blood Relatives of ' + person.name()
    return render(request,
                  'people/relatives.html',
                  {'title': title, 'relatives': person.relatives(), 'list': Person.objects.all()})


def descendants(request, person_id):
    person = get_object_or_404(Person, id=person_id)
    title = 'Descendants of ' + person.name()
    return render(request,
                  'people/relatives.html',
                  {'title': title,
                   'relatives': person.annotated_descendants(),
                   'list': Person.objects.all()})


def ancestors(request, person_id):
    person = get_object_or_404(Person, id=person_id)
    title = 'Ancestors of ' + person.name()
    return render(request,
                  'people/relatives.html',
                  {'title': title,
                   'relatives': person.annotated_ancestors(),
                   'list': Person.objects.all()})


def ancestors_report(request, person_id):
    '''Count how many known ancestors the given person has in each previous
    generation so that we know how many ancestors remain unknown.'''
    person = get_object_or_404(Person, id=person_id)
    ancestors = person.annotated_ancestors()
    generation_counts = [(g, len(list(m)), int(pow(2, g)))
                         for g, m in groupby(ancestors, itemgetter(2))]
    title = 'Known Ancestors of ' + person.name()
    return render(request,
                  'people/report.html',
                  {'generation_counts': generation_counts,
                   'title': title,
                   'list': Person.objects.all()})


def location(request, location_id):
    location = get_object_or_404(Location, id=location_id)
    title = 'People born in ' + location.name
    return render(request,
                  'people/people.html',
                  {'title': title, 'people': location.natives.all(), 'list': Person.objects.all()})


def region(request, region_name):
    people = Person.objects.filter(birth_location__county_state_province=region_name)
    title = 'People born in ' + region_name
    return render(request,
                  'people/people.html',
                  {'title': title, 'people': people, 'list': Person.objects.all()})


def surname(request, surname):
    people = Person.objects.filter(Q(surname=surname) | Q(maiden_name=surname))
    title = 'People with the surname ' + surname
    return render(request,
                  'people/people.html',
                  {'title': title, 'people': people, 'list': Person.objects.all()})


def tag(request, slug):
    people = Person.objects.filter(tags__slug=slug)
    title = 'People tagged "{0}"'.format(slug)
    return render(request,
                  'people/people.html',
                  {'title': title, 'people': people, 'list': Person.objects.all()})
