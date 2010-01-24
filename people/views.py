from django.shortcuts import render_to_response
from familytree.people.models import Person

def person(request, person_id):
    person = Person.objects.get(id=person_id)
    return render_to_response('person.html', {'person': person})
