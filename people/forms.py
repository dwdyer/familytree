from django import forms
from people.models import Person

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
    '''Custom version of the choice field that formats the user and their birth
    year in a way that can be interpreted by the client-side JavaScript.'''
    def label_from_instance(self, obj):
        if obj.date_of_birth():
            return '{0}|{1}'.format(obj.name(), obj.date_of_birth().year)
        else:
            return obj.name()


class AddPersonForm(BootstrapModelForm):
    
    class Meta:
        model = Person
        fields = ['gender', 'deceased', 'blood_relative',
                  'forename', 'middle_names', 'known_as', 'surname', 'maiden_name',
                  'mother', 'father', 'notes']
        field_classes = {'mother': PersonChoiceField,
                         'father': PersonChoiceField}
        widgets = {'gender': forms.RadioSelect}
