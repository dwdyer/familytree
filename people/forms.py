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


class AddPersonForm(BootstrapModelForm):
    
    class Meta:
        model = Person
        fields = ['gender', 'deceased', 'blood_relative',
                  'forename', 'middle_names', 'known_as', 'surname', 'maiden_name',
                  'mother', 'father', 'notes']
        widgets = {'gender': forms.RadioSelect}
