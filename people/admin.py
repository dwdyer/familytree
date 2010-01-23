from familytree.people.models import Person
from django import forms
from django.contrib import admin

class PersonForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PersonForm, self).__init__(*args, **kwargs)
        # Restrict suggested parents to members of the appropriate gender born before this person.
        self.fields['mother'].queryset = Person.objects.filter(gender = 'F', date_of_birth__lt=self.instance.date_of_birth)
        self.fields['father'].queryset = Person.objects.filter(gender = 'M', date_of_birth__lt=self.instance.date_of_birth)

class PersonAdmin(admin.ModelAdmin):
    form = PersonForm

admin.site.register(Person, PersonAdmin)
