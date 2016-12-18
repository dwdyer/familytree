from datetime import date
from django.core.urlresolvers import reverse
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from itertools import chain, groupby
from math import pow
from operator import attrgetter, itemgetter
from people.forms import AddPersonForm
from people.models import Location, Person, Marriage, Event
from people.relations import describe_relative
from taggit.models import Tag

def index(request):
    regions = Location.objects.raw('''SELECT ANY_VALUE(l.id) AS id, l.county_state_province AS name, c.name AS country_name,
                                      c.country_code AS country_code, count(1) AS natives_count
                                      FROM people_location l, people_person p, people_event e, people_country c
                                      WHERE p.birth_id = e.id AND e.location_id = l.id AND l.country_id = c.id AND p.blood_relative = 1
                                      GROUP BY l.county_state_province, c.id
                                      ORDER BY count(1) DESC, l.county_state_province LIMIT 10''')

    surnames = Person.objects.filter(blood_relative=True).values('surname').annotate(Count('surname'))
    surnames = surnames.filter(surname__count__gte=2).order_by('surname')
    males = Person.objects.filter(gender='M', blood_relative=True)
    male_names = males.values('forename').annotate(Count('forename')).order_by('-forename__count', 'forename')
    females = Person.objects.filter(gender='F', blood_relative=True)
    female_names = females.values('forename').annotate(Count('forename')).order_by('-forename__count', 'forename')

    locations = Location.objects.raw('''SELECT l.id, l.name, l.latitude, l.longitude, COUNT(l.id) AS natives_count
                                        FROM people_person p, people_event e, people_location l
                                        WHERE p.birth_id = e.id AND e.location_id = l.id AND p.blood_relative
                                        AND l.latitude IS NOT NULL AND l.longitude IS NOT NULL
                                        GROUP BY l.id''')
    min_lat = min_lng = 90
    max_lat = max_lng = -90
    for location in locations:
        min_lat = min(location.latitude, min_lat)
        max_lat = max(location.latitude, max_lat)
        min_lng = min(location.longitude, min_lng)
        max_lng = max(location.longitude, max_lng)

    tags = Tag.objects.annotate(tag_count=Count('taggit_taggeditem_items')).order_by('name')

    # On this day
    today = date.today()
    lookup = today.strftime('-%m-%d')
    events = sorted(chain(Event.objects.filter(date__endswith=lookup),
                          Marriage.objects.filter(date__endswith=lookup)),
                    key=attrgetter('date'))

    return render(request,
                  'people/index.html',
                  {'surnames': surnames,
                   'male_names': male_names[:10],
                   'female_names': female_names[:10],
                   'regions': regions,
                   'locations': locations,
                   'tags': tags,
                   'map_area' : ((min_lat, min_lng), (max_lat, max_lng)),
                   'today': today,
                   'on_this_day': events,
                   'list': Person.objects.select_related('birth')})


def person(request, person_id):
    person = get_object_or_404(Person, id=person_id)
    relationship = describe_relative(request.user.person,
                                     person,
                                     request.user.person._ancestor_distances(),
                                     person._ancestor_distances()) if request.user.person else None
    return render(request,
                  'people/person.html',
                  {'person': person,
                   'descendants': len(list(person.descendants())),
                   'ancestors': len(list(person.ancestors())),
                   'relationship': relationship,
                   'list': Person.objects.select_related('birth')})


def relatives(request, person_id):
    person = get_object_or_404(Person, id=person_id)
    title = 'Blood Relatives of ' + person.name()
    map_link = reverse('relatives_map', args=[person_id])
    return render(request,
                  'people/relatives.html',
                  {'title': title,
                   'relatives': person.annotated_relatives(),
                   'map_link': map_link,
                   'list': Person.objects.select_related('birth')})


def descendants(request, person_id):
    person = get_object_or_404(Person, id=person_id)
    title = 'Descendants of ' + person.name()
    map_link = reverse('descendants_map', args=[person_id])
    return render(request,
                  'people/relatives.html',
                  {'title': title,
                   'relatives': person.annotated_descendants(),
                   'map_link': map_link,
                   'list': Person.objects.select_related('birth')})


def ancestors(request, person_id):
    person = get_object_or_404(Person, id=person_id)
    title = 'Ancestors of ' + person.name()
    map_link = reverse('ancestors_map', args=[person_id])
    return render(request,
                  'people/relatives.html',
                  {'title': title,
                   'person': person,
                   'relatives': person.annotated_ancestors(),
                   'map_link': map_link,
                   'list': Person.objects.select_related('birth')})


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
                   'person': person,
                   'generation_counts': generation_counts,
                   'missing_parents': missing_parents,
                   'list': Person.objects.select_related('birth')})


def ancestors_map(request, person_id):
    person = get_object_or_404(Person, id=person_id)
    title = 'Ancestors of ' + person.name() + ' - Map of Birth Places'
    return _people_map(request, person.ancestors(), title)


def ring_chart(request, person_id):
    person = get_object_or_404(Person, id=person_id)
    return render(request,
                  'people/ringchart.html',
                  {'person': person, 'list': Person.objects.select_related('birth')}) 


def ring_chart_svg(request, person_id):
    person = get_object_or_404(Person, id=person_id)
    rings = [[person]]
    while True:
        (ring, count) = _next_ring(rings[-1])
        if (count > 0):
            rings.append(ring)
        else:
            break
    return render(request,
                  'people/ringchart.svg',
                  {'rings': list(reversed(rings))},
                  content_type='image/svg+xml')


def _next_ring(previous_ring):
    '''Returns a full ring of ancestors, with None used as a placeholder for
    those who are unknown. Also returns the count of how many non-None people
    are in the ring.'''
    ring = []
    count = 0
    for person in previous_ring:
        if person is None:
            ring.extend([None, None])
        else:
            ring.append(person.mother)
            ring.append(person.father)
            count += (1 if person.father else 0) + (1 if person.mother else 0)
    # Make sure the list has an entry for evey position.
    ring.extend([None] * ((len(previous_ring) * 2) - len (ring)))
    return (ring, count)


def descendants_map(request, person_id):
    person = get_object_or_404(Person, id=person_id)
    title = 'Descendants of ' + person.name() + ' - Map of Birth Places'
    return _people_map(request, person.descendants(), title)


def relatives_map(request, person_id):
    person = get_object_or_404(Person, id=person_id)
    title = 'Blood Relatives of ' + person.name() + ' - Map of Birth Places'
    return _people_map(request, person.relatives(), title)


def _people_map(request, people, title):
    counts = {}
    min_lat = min_lng = 90
    max_lat = max_lng = -90
    for person in people:
        location = person.birth_location()
        if location and location.latitude and location.longitude:
            count = counts.get(location, 0)
            counts[location] = count + 1
            min_lat = min(location.latitude, min_lat)
            max_lat = max(location.latitude, max_lat)
            min_lng = min(location.longitude, min_lng)
            max_lng = max(location.longitude, max_lng)
    for location in counts.keys():
        location.natives_count = counts.get(location)
    return render(request,
                  'people/map.html',
                  {'title': title,
                   'locations': counts.keys(),
                   'map_area' : ((min_lat, min_lng), (max_lat, max_lng)),
                   'list': Person.objects.select_related('birth')})


def location(request, location_id):
    location = get_object_or_404(Location, id=location_id)
    births = Person.objects.filter(birth__location=location)
    marriages = Marriage.objects.filter(location=location)
    deaths = Person.objects.filter(death__location=location)
    return render(request,
                  'people/location.html',
                  {'location': location,
                   'births': births,
                   'marriages': marriages,
                   'deaths': deaths,
                   'list': Person.objects.select_related('birth')})


def region(request, region_name):
    people = Person.objects.filter(birth__location__county_state_province=region_name)
    title = 'People born in ' + region_name
    return render(request,
                  'people/people.html',
                  {'title': title,
                   'people': people,
                   'list': Person.objects.select_related('birth')})


def surname(request, surname):
    people = Person.objects.filter(Q(surname=surname) | Q(maiden_name=surname))
    title = 'People with the surname ' + surname
    return render(request,
                  'people/people.html',
                  {'title': title,
                   'people': people,
                   'list': Person.objects.select_related('birth')})


def forename(request, forename):
    people = Person.objects.filter(Q(forename=forename) | Q(middle_names__contains=forename))
    title = 'People with the given name ' + forename
    return render(request,
                  'people/people.html',
                  {'title': title,
                   'people': people,
                   'list': Person.objects.select_related('birth')})


def tag(request, slug):
    people = Person.objects.filter(tags__slug=slug)
    title = 'People tagged "{0}"'.format(slug)
    return render(request,
                  'people/people.html',
                  {'title': title,
                   'people': people,
                   'list': Person.objects.select_related('birth')})


def add_person(request):
    if request.method == 'POST':
        form = AddPersonForm(request.POST)
        if form.is_valid():
            person = form.save()
            # TO DO:
            return redirect(reverse('person', kwargs={'person_id': person.id}))
    else:
        form = AddPersonForm()
    return render(request,
                  'people/add.html',
                  {'form': form,
                   'list': Person.objects.select_related('birth')})
