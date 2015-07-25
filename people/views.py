from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render
from itertools import groupby
from math import pow
from operator import itemgetter
from people.models import Location, Person

def index(request):
    regions = Location.objects.raw('''SELECT l.id, l.county_state_province AS name, c.name AS country_name,
                                      c.country_code AS country_code, count(1) AS natives_count
                                      FROM people_location l, people_person p, people_country c
                                      WHERE p.birth_location_id = l.id AND l.country_id = c.id AND p.blood_relative = 1
                                      GROUP BY l.county_state_province, c.id
                                      ORDER BY count(1) DESC, l.county_state_province LIMIT 10''')

    surnames = Person.objects.filter(blood_relative=True).values('surname').annotate(Count('surname'))
    surnames = surnames.filter(surname__count__gte=2).order_by('surname')
    males = Person.objects.filter(gender='M', blood_relative=True)
    male_names = males.values('forename').annotate(Count('forename')).order_by('-forename__count', 'forename')
    females = Person.objects.filter(gender='F', blood_relative=True)
    female_names = females.values('forename').annotate(Count('forename')).order_by('-forename__count', 'forename')

    locations = Location.objects.raw('''SELECT l.id, l.name, l.latitude, l.longitude, COUNT(l.id) AS natives_count
                                        FROM people_person p, people_location l
                                        WHERE p.birth_location_id = l.id AND p.blood_relative
                                        AND l.latitude IS NOT NULL AND l.longitude IS NOT NULL
                                        GROUP BY l.id''')
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
                   'male_names': male_names[:10],
                   'female_names': female_names[:10],
                   'regions': regions,
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
                  {'title': title,
                   'relatives': person.relatives(),
                   'list': Person.objects.all()})


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
                   'person': person,
                   'relatives': person.annotated_ancestors(),
                   'list': Person.objects.all()})


def ancestors_report(request, person_id):
    '''Count how many known ancestors the given person has in each previous
    generation so that we know how many ancestors remain unknown.'''
    person = get_object_or_404(Person, id=person_id)
    ancestors = person.annotated_ancestors()
    generation_counts = [(g, len(list(m)), int(pow(2, g)))
                         for g, m in groupby(ancestors, itemgetter(2))]
    missing_parents = [(p, r, p.mother is None, p.father is None)
                       for p, r, d in ancestors if not (p.mother and p.father)]
    title = 'Known Ancestors of ' + person.name()
    return render(request,
                  'people/report.html',
                  {'title': title,
                   'generation_counts': generation_counts,
                   'missing_parents': missing_parents,
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


def forename(request, forename):
    people = Person.objects.filter(Q(forename=forename) | Q(middle_names__contains=forename))
    title = 'People with the given name ' + forename
    return render(request,
                  'people/people.html',
                  {'title': title, 'people': people, 'list': Person.objects.all()})


def tag(request, slug):
    people = Person.objects.filter(tags__slug=slug)
    title = 'People tagged "{0}"'.format(slug)
    return render(request,
                  'people/people.html',
                  {'title': title, 'people': people, 'list': Person.objects.all()})
