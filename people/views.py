from django.shortcuts import render_to_response
from familytree.people.models import Person

def person(request, person_id):
    person = Person.objects.get(id=person_id)
    return render_to_response('person.html', {'person': person})

def relatives(request, person_id):
    person = Person.objects.get(id=person_id)
    title = 'Blood Relatives of ' + person.name()
    return render_to_response('relatives.html', {'title': title, 'relatives': person.relatives()})

def descendants(request, person_id):
    person = Person.objects.get(id=person_id)
    title = 'Descendants of ' + person.name()
    return render_to_response('relatives.html', {'title': title, 'relatives': person.descendants()})

def ancestors(request, person_id):
    person = Person.objects.get(id=person_id)
    title = 'Ancestors of ' + person.name()
    return render_to_response('relatives.html', {'title': title, 'relatives': person.ancestors()})
