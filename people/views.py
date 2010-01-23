from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse
from familytree.people.models import Person

def person(request, person_id):
    person = Person.objects.get(id=person_id)
    template = get_template('person.html')
    html = template.render(Context({'person': person}))
    return HttpResponse(html)
