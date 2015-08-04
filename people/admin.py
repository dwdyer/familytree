from people.models import Country, Location, Person, Marriage, Photograph, Document
from django import forms
from django.contrib import admin

class PersonAdmin(admin.ModelAdmin):
    fieldsets = [(None, {'fields': [('forename', 'middle_names'),
                                    ('surname', 'maiden_name'),
                                    ('gender', 'blood_relative'),
                                    ('date_of_birth', 'birth_location'),
                                    ('deceased', 'date_of_death'),
                                    ('mother', 'father'),
                                    'notes',
                                    'tags']})]
    list_display = ['surname', 'name', 'gender', 'date_of_birth', 'birth_location', 'deceased']
    list_display_links = ['name']
    list_editable = ['date_of_birth', 'birth_location']
    list_filter = ['blood_relative', 'gender', 'deceased', 'surname']
    search_fields = ['surname', 'forename', 'middle_names', 'maiden_name']
admin.site.register(Person, PersonAdmin)


class PhotographAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.base_fields['people'].widget = admin.widgets.FilteredSelectMultiple('people', False)
        super(PhotographAdminForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Photograph
        fields = '__all__'

class PhotographAdmin(admin.ModelAdmin):
    form = PhotographAdminForm
    list_display = ['__unicode__', 'caption']
admin.site.register(Photograph, PhotographAdmin)


class DocumentAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.base_fields['people'].widget = admin.widgets.FilteredSelectMultiple('people', False)
        super(DocumentAdminForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Document
        fields = '__all__'

class DocumentAdmin(admin.ModelAdmin):
    form = DocumentAdminForm
    list_display = ['title']
admin.site.register(Document, DocumentAdmin)


class MarriageAdmin(admin.ModelAdmin):
    list_display = ['husband', 'wife', 'wedding_date', 'wedding_location', 'divorced']
    list_display_links = ['husband', 'wife']
    list_editable = ['wedding_date', 'wedding_location', 'divorced']
    search_fields = ['husband__surname', 'husband__forename', 'wife__maiden_name', 'wife__forename']
admin.site.register(Marriage, MarriageAdmin)


class LocationInline(admin.TabularInline):
    model = Location

class CountryAdmin(admin.ModelAdmin):
    list_display = ['name', 'country_code']
    inlines = [LocationInline]
admin.site.register(Country, CountryAdmin)


class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'county_state_province', 'country', 'latitude', 'longitude']
    list_filter = ['country']
    search_fields = ['name', 'county_state_province', 'country__name']
admin.site.register(Location, LocationAdmin)
