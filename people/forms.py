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


class CountryChoiceField(forms.ModelChoiceField):
    '''Custom version of the choice field that formats a country in a way that
    can be interpreted by the client-side JavaScript.'''
    def label_from_instance(self, obj):
        return '{0}|{1}'.format(obj.name, obj.country_code)


class AddPersonForm(BootstrapModelForm):
    date_of_birth = UncertainDateFormField(label='Date of birth', help_text='Date of birth', required=False)
    birth_location = LocationChoiceField(label='Birthplace', queryset=Location.objects.all(), required=False)
    birth_reference = forms.URLField(label='Reference', help_text='Reference URL (optional)', required=False)

    date_of_baptism = UncertainDateFormField(label='Baptism date', help_text='Baptism date', required=False)
    baptism_location = LocationChoiceField(label='Location', queryset=Location.objects.all(), required=False)
    baptism_reference = forms.URLField(label='Reference', help_text='Reference URL (optional)', required=False)

    date_of_death = UncertainDateFormField(label='Date of death', help_text='Date of death', required=False)
    death_location = LocationChoiceField(label='Location', queryset=Location.objects.all(), required=False)
    death_reference = forms.URLField(label='Reference', help_text='Reference URL (optional)', required=False)

    date_of_burial = UncertainDateFormField(label='Burial date', help_text='Burial date', required=False)
    burial_location = LocationChoiceField(label='Location', queryset=Location.objects.all(), required=False)
    burial_reference = forms.URLField(label='Reference', help_text='Reference URL (optional)', required=False)

    def save(self, commit=True, *args, **kwargs):
        with transaction.atomic():
            person = super(AddPersonForm, self).save(commit=commit, *args, **kwargs)
            self._update_event(person, Event.BIRTH, 'date_of_birth', 'birth_location', 'birth_reference')
            self._update_event(person, Event.BAPTISM, 'date_of_baptism', 'baptism_location', 'baptism_reference')
            self._update_event(person, Event.DEATH, 'date_of_death', 'death_location', 'death_reference')
            self._update_event(person, Event.BURIAL, 'date_of_burial', 'burial_location', 'burial_reference')
            return person

    def _update_event(self, person, event_type, date_field, location_field, reference_field):
        event = person.events.filter(event_type=event_type).first()
        if self.cleaned_data[date_field]:
            if event:
                event.date = self.cleaned_data[date_field]
                event.location = self.cleaned_data[location_field]
                event.reference = self.cleaned_data[reference_field]
            else:
                event = Event(person=person,
                              event_type=event_type,
                              date=self.cleaned_data[date_field],
                              location=self.cleaned_data[location_field],
                              reference=self.cleaned_data[reference_field])
            event.save()
        elif event:
            event.delete()

    class Meta:
        model = Person
        fields = ['gender', 'deceased', 'blood_relative',
                  'forename', 'middle_names', 'known_as', 'surname', 'maiden_name',
                  'mother', 'father', 'notes', 'tags']
        field_classes = {'mother': PersonChoiceField,
                         'father': PersonChoiceField}
        widgets = {'gender': forms.RadioSelect}


class EditPersonForm(AddPersonForm):

    def __init__(self, *args, **kwargs):
        super(EditPersonForm, self).__init__(*args, **kwargs)
        instance = kwargs['instance']
        if instance.birth:
            self.fields['date_of_birth'].initial = instance.birth.date
            self.fields['birth_location'].initial = instance.birth.location
            self.fields['birth_reference'].initial = instance.birth.reference
        if instance.death:
            self.fields['date_of_death'].initial = instance.death.date
            self.fields['death_location'].initial = instance.death.location
            self.fields['death_reference'].initial = instance.death.reference
        baptism = instance.events.filter(event_type=Event.BAPTISM).first()
        if baptism:
            self.fields['date_of_baptism'].initial = baptism.date
            self.fields['baptism_location'].initial = baptism.location
            self.fields['baptism_reference'].initial = baptism.reference
        burial = instance.events.filter(event_type=Event.BURIAL).first()
        if burial:
            self.fields['date_of_burial'].initial = burial.date
            self.fields['burial_location'].initial = burial.location
            self.fields['burial_reference'].initial = burial.reference


class AddLocationForm(BootstrapModelForm):

    class Meta:
        model = Location
        fields = ['name', 'county_state_province', 'country']
        field_classes = {'country': CountryChoiceField}


# Custom parsing for tags (don't use spaces as separators).
def tag_comma_splitter(tag_string):
    return [t.strip() for t in tag_string.split(',') if t.strip()]

def tag_comma_joiner(tags):
    return ', '.join(t.name for t in tags)
