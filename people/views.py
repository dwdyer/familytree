from collections import defaultdict
from datetime import date
from django.contrib.auth.decorators import user_passes_test
from django.core.serializers import serialize
from django.core.urlresolvers import reverse
from django.db import connection
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from itertools import chain, groupby
from math import pow
from operator import attrgetter, itemgetter
from people.fields import UncertainDate
from people.forms import AddLocationForm, AddPersonForm, EditPersonForm
from people.models import Location, Person, Marriage, Event, SurnameVariant
from people.relations import describe_relative
from stronghold.decorators import public
from taggit.models import Tag
import json

@public
def index(request):
    if not request.user.is_authenticated:
        return redirect(reverse('surnames'))

    regions = Location.objects.raw('''SELECT ANY_VALUE(l.id) AS id, l.county_state_province AS name, c.name AS country_name,
                                      c.country_code AS country_code, count(1) AS natives_count
                                      FROM people_location l, people_person p, people_event e, people_country c
                                      WHERE p.birth_id = e.id AND e.location_id = l.id AND l.country_id = c.id AND p.blood_relative = 1
                                      GROUP BY l.county_state_province, c.id
                                      ORDER BY count(1) DESC, l.county_state_province LIMIT 10''')

    surnames = _surnames()
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

    tags = Tag.objects.all().order_by('name')

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

def _surnames():
    query = '''SELECT surname, n AS count, v FROM
                 (SELECT IFNULL(canonical, surname) AS surname, COUNT(1) AS n, MAX(canonical IS NOT NULL) AS V
                  FROM people_person LEFT JOIN people_surnamevariant ON variant=surname
                  WHERE blood_relative=1 GROUP BY IFNULL(canonical, surname) ORDER BY surname)
               AS surnames WHERE n >= 2'''
    with connection.cursor() as cursor:
        cursor.execute(query)
        return [(s[0], s[1], s[2]) for s in cursor.fetchall()]


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


def ancestors_report_undead(request, person_id):
    person = get_object_or_404(Person, id=person_id)
    people = [p for p in person.ancestors() if p.deceased and p.death == None]
    title = 'Deceased ancestors of {0} with unknown death details'.format(person.name())
    return render(request,
                  'people/people.html',
                  {'title': title,
                   'people': people,
                   'list': Person.objects.select_related('birth')})


def ancestors_report_maiden_names(request, person_id):
    person = get_object_or_404(Person, id=person_id)
    people = [p for p in person.ancestors() if p.has_missing_maiden_name()]
    title = 'Married female ancestors of {0} with unknown maiden names'.format(person.name())
    return render(request,
                  'people/people.html',
                  {'title': title,
                   'people': people,
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
    while len(rings) < 10:
        (ring, count) = _next_ring(rings[-1])
        rings.append(ring)
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


def descendants_tree(request, person_id):
    person = get_object_or_404(Person, id=person_id)
    return render(request,
                  'people/tree.html',
                  {'person': person, 'list': Person.objects.select_related('birth')})


def descendants_tree_svg(request, person_id):
    person = get_object_or_404(Person, id=person_id)
    generations = defaultdict(list)
    for (gen, column, person) in _generations(person, 0, 0):
        generations[gen].append((column, person))
    return render(request, 'people/tree.svg', {'person': person, 'generations': generations.values()})

def _generations(person, gen, column):
    yield (gen, column, person)
    for col, child in enumerate(person.children()):
        yield from _generations(child, gen + 1, column + col)


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
    try:
        canonical = SurnameVariant.objects.get(variant=surname).canonical
    except SurnameVariant.DoesNotExist:
        canonical = surname
    variants = SurnameVariant.objects.filter(canonical=canonical).values_list('variant', flat=True)
    all_variants = [canonical] + list(variants)
    people = Person.objects.filter(Q(surname__in=all_variants) | Q(maiden_name__in=all_variants))
    title = 'People with the surname ' + '/'.join(all_variants)
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

def alive_in_year(request, year):
    year_start = UncertainDate(int(year), 1, 1)
    year_end = UncertainDate(int(year), 12, 31)
    hundred_years_earlier = UncertainDate(int(year) - 100, 1, 1)
    hundred_years_later = UncertainDate(int(year) + 100, 12, 31)
    born_before = Q(birth__date__lte=year_start) | Q(birth__date=None, death__date__lte=hundred_years_later)
    died_after = Q(death__date__gte=year_end) | Q(deceased=False) | Q(death__date=None, birth__date__gte=hundred_years_earlier)
    people = Person.objects.filter(born_before, died_after)
    title = 'People alive (or possibly alive) in {0}'.format(year)
    return render(request,
                  'people/people.html',
                  {'title': title,
                   'people': people,
                   'list': Person.objects.select_related('birth')})


def _staff_only(user):
    return user.is_staff

@user_passes_test(_staff_only)
def add_person(request):
    if request.method == 'POST':
        form = AddPersonForm(request.POST)
        if form.is_valid():
            person = form.save()
            return redirect(reverse('person', kwargs={'person_id': person.id}))
    else:
        form = AddPersonForm()
    return render(request,
                  'people/add.html',
                  {'form': form,
                   'location_form': AddLocationForm(),
                   'list': Person.objects.select_related('birth')})


@user_passes_test(_staff_only)
def edit_person(request, person_id):
    person = get_object_or_404(Person, id=person_id)
    if request.method == 'POST':
        form = EditPersonForm(request.POST, instance=person)
        if form.is_valid():
            person = form.save()
            return redirect(reverse('person', kwargs={'person_id': person.id}))
    else:
        form = EditPersonForm(instance=person)
    return render(request,
                  'people/edit.html',
                  {'form': form,
                   'location_form': AddLocationForm(),
                   'list': Person.objects.select_related('birth')})


@user_passes_test(_staff_only)
@require_POST
def add_location(request):
    form = AddLocationForm(request.POST)
    if form.is_valid():
        location = form.save()
        return HttpResponse('{0}|{1}|{2}'.format(location.id, str(location), location.country.country_code)) # 200 OK
    return HttpResponse(json.dumps(form.errors), content_type='application/json', status=422)


@public
def surnames(request):
    with connection.cursor() as cursor:
        # List all surnames for non-living blood relatives born over 100 years ago, where at least
        # two people share that name.
        today = date.today()
        hundred_years_ago = date(today.year - 100, today.month, today.day)
        cursor.execute('''SELECT s AS surname FROM
                          (SELECT IF(maiden_name != '' AND maiden_name IS NOT NULL, maiden_name, surname) AS s, COUNT(1) AS n
                           FROM people_person p LEFT JOIN people_event e
                           ON (e.person_id = p.id AND e.event_type = 0)
                           WHERE deceased = 1 AND blood_relative = 1
                           AND (date = '' OR date IS NULL OR date < '{0}') GROUP BY s)
                          AS surnames WHERE n >= 2'''.format(hundred_years_ago))
        surnames = [(s[0], _locations_for_surname(s[0])) for s in cursor.fetchall()]
    return render(request,
                  'people/surnames.html',
                  {'surnames': surnames,
                   'list': Person.objects.select_related('birth')})

def _locations_for_surname(surname):
    surname_filter = Q(events__person__maiden_name=surname) | (Q(events__person__maiden_name='') & Q(events__person__surname=surname))
    locations = Location.objects.filter(surname_filter,
                                        events__event_type__in=[0, 3],
                                        events__person__blood_relative=True,
                                        events__person__deceased=True)
    # Exclude places that only relate to a single individual, unless that place is the
    # only one we know for anybody with that surname.
    if locations.count() > 1:
        locations = locations.annotate(Count('id')).filter(id__count__gte=2)
    return locations.distinct()
