from django import forms
from django.db import transaction
from people.fields import UncertainDateFormField
from people.models import Event, Location, Person

class BootstrapModelForm(forms.ModelForm):
    '''Convenient base class for applying Bootstrap CSS classes to fields in
       ModelForms.'''
    def __init__(self, *args, **kwargs):
        super(BootstrapModelForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                if type(field.widget) not in [forms.CheckboxInput, forms.RadioSelect]:
                    field.widget.attrs['class'] = 'form-control'
                    field.widget.attrs['placeholder'] = field.help_text


class PersonChoiceField(forms.ModelChoiceField):
    '''Custom version of the choice field that formats a person and their birth
    year in a way that can be interpreted by the client-side JavaScript.'''
    def label_from_instance(self, obj):
        if obj.date_of_birth():
            return '{0}|{1}'.format(obj.name(), obj.date_of_birth().year)
        else:
            return obj.name()


class LocationChoiceField(forms.ModelChoiceField):
    '''Custom version of the choice field that formats a location in a way that
    can be interpreted by the client-side JavaScript.'''
    def label_from_instance(self, obj):
        return '{0}|{1}'.format(str(obj), obj.country.country_code)


class AddPersonForm(BootstrapModelForm):
    date_of_birth = UncertainDateFormField(label='Date of birth', help_text='Date of birth', required=False)
    birth_location = LocationChoiceField(label='Birthplace', queryset=Location.objects.all(), required=False)
    birth_reference = forms.URLField(label='Reference', help_text='Reference URL (optional)', required=False)

    date_of_death = UncertainDateFormField(label='Date of death', help_text='Date of death', required=False)
    death_location = LocationChoiceField(label='Location', queryset=Location.objects.all(), required=False)
    death_reference = forms.URLField(label='Reference', help_text='Reference URL (optional)', required=False)

    def save(self, commit=True, *args, **kwargs):
        with transaction.atomic():
            person = super(AddPersonForm, self).save(commit=commit, *args, **kwargs)

            if self.cleaned_data['date_of_birth'] or self.cleaned_data['birth_location']:
                birth = Event(person=person,
                              event_type=Event.BIRTH,
                              date=self.cleaned_data['date_of_birth'],
                              location=self.cleaned_data['birth_location'],
                              reference=self.cleaned_data['birth_reference'])
                birth.save()

            if self.cleaned_data['date_of_death'] or self.cleaned_data['death_location']:
                death = Event(person=person,
                              event_type=Event.DEATH,
                              date=self.cleaned_data['date_of_death'],
                              location=self.cleaned_data['death_location'],
                              reference=self.cleaned_data['death_reference'])
                death.save()
            return person

    class Meta:
        model = Person
        fields = ['gender', 'deceased', 'blood_relative',
                  'forename', 'middle_names', 'known_as', 'surname', 'maiden_name',
                  'mother', 'father', 'notes']
        field_classes = {'mother': PersonChoiceField,
                         'father': PersonChoiceField}
        widgets = {'gender': forms.RadioSelect}
