from django.db.models import Count, Q
from django.shortcuts import render
from people.models import Location, Person

def index(request):
    regions = Location.objects.values('county_state_province',
                                      'country__name',
                                      'country__country_code')
    regions = regions.annotate(Count('natives')).order_by('-natives__count',
                                                          'county_state_province')
    surnames = Person.objects.values('surname').annotate(Count('surname'))
    surnames = surnames.filter(surname__count__gte=2).order_by('surname')
    return render(request,
                  'people/index.html',
                  {'surnames': surnames, 'regions': regions[:10]})


def person(request, person_id):
    person = Person.objects.get(id=person_id)
    return render(request, 'people/person.html', {'person': person})


def relatives(request, person_id):
    person = Person.objects.get(id=person_id)
    title = 'Blood Relatives of ' + person.name()
    return render(request,
                  'people/relatives.html',
                  {'title': title, 'relatives': person.relatives()})


def descendants(request, person_id):
    person = Person.objects.get(id=person_id)
    title = 'Descendants of ' + person.name()
    return render(request,
                  'people/relatives.html',
                  {'title': title, 'relatives': person.annotated_descendants()})


def ancestors(request, person_id):
    person = Person.objects.get(id=person_id)
    title = 'Ancestors of ' + person.name()
    return render(request,
                  'people/relatives.html',
                  {'title': title, 'relatives': person.annotated_ancestors()})


def region(request, region_name):
    people = Person.objects.filter(birth_location__county_state_province=region_name)
    title = 'People born in ' + region_name
    return render(request, 'people/people.html', {'title': title, 'people': people})


def surname(request, surname):
    people = Person.objects.filter(Q(surname=surname) | Q(maiden_name=surname))
    title = 'People with the surname ' + surname
    return render(request, 'people/people.html', {'title': title, 'people': people})


def tag(request, slug):
    people = Person.objects.filter(tags__slug=slug)
    title = 'People tagged "{0}"'.format(slug)
    return render(request, 'people/people.html', {'title': title, 'people': people})
