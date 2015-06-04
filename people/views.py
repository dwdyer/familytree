from django.shortcuts import render_to_response
from people.models import Person

def person(request, person_id):
    person = Person.objects.get(id=person_id)
    return render_to_response('people/person.html', {'person': person})

def relatives(request, person_id):
    person = Person.objects.get(id=person_id)
    title = 'Blood Relatives of ' + person.name()
    return render_to_response('people/relatives.html',
                              {'title': title, 'relatives': person.relatives()})

def descendants(request, person_id):
    person = Person.objects.get(id=person_id)
    title = 'Descendants of ' + person.name()
    return render_to_response('people/relatives.html',
                              {'title': title, 'relatives': person.annotated_descendants()})

def ancestors(request, person_id):
    person = Person.objects.get(id=person_id)
    title = 'Ancestors of ' + person.name()
    return render_to_response('people/relatives.html',
                              {'title': title, 'relatives': person.annotated_ancestors()})
