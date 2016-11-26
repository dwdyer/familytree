from people.models import Country, Location, Person, Marriage, Photograph, Document, Event
from django import forms
from django.contrib import admin

class FamilyTreeAdminSite(admin.AdminSite):
    def each_context(self, request):
        context = super(FamilyTreeAdminSite, self).each_context(request)
        context['list'] = Person.objects.all()
        return context


class HasReferenceFilter(admin.SimpleListFilter):
    title = 'has reference'
    parameter_name = 'has_url'

    def lookups(self, request, model_admin):
        return [('yes', 'Yes'), ('no', 'No')]

    def queryset(self, request, queryset):
        filter_option = self.value()
        if filter_option == 'yes':
            return queryset.filter(reference__isnull=False).exclude(reference='')
        elif filter_option == 'no':
            return queryset.filter(reference='')
        else:
            return queryset

class EventAdmin(admin.ModelAdmin):
    list_display = ['short_date', 'event_type', 'person', 'location']
    list_filter = ['event_type', HasReferenceFilter]


class EventInline(admin.TabularInline):
    model = Event
    extra = 1

class BaptismFilter(admin.SimpleListFilter):
    title = 'has baptism record'
    parameter_name = 'baptism'

    def lookups(self, request, model_admin):
        return [('yes', 'Yes'), ('no', 'No')]

    def queryset(self, request, queryset):
        filter_option = self.value()
        if filter_option == 'yes':
            return queryset.filter(events__event_type__name='Baptism')
        elif filter_option == 'no':
            return queryset.exclude(events__event_type__name='Baptism')
        else:
            return queryset

class BurialFilter(admin.SimpleListFilter):
    title = 'has burial record'
    parameter_name = 'burial'

    def lookups(self, request, model_admin):
        return [('yes', 'Yes'), ('no', 'No')]

    def queryset(self, request, queryset):
        filter_option = self.value()
        if filter_option == 'yes':
            return queryset.filter(events__event_type__name='Burial')
        elif filter_option == 'no':
            return queryset.exclude(events__event_type__name='Burial')
        else:
            return queryset

class PersonAdmin(admin.ModelAdmin):
    fieldsets = [(None, {'fields': [('forename', 'middle_names'),
                                    ('surname', 'maiden_name'),
                                    ('gender', 'blood_relative'),
                                    ('date_of_birth', 'birth_location'),
                                    ('deceased', 'date_of_death'),
                                    ('mother', 'father'),
                                    'notes',
                                    ('tags', 'user')]})]
    list_display = ['surname', 'name', 'gender', 'date_of_birth', 'birth_location', 'deceased']
    list_display_links = ['name']
    list_editable = ['date_of_birth', 'birth_location']
    list_filter = ['blood_relative', 'gender', 'deceased', BaptismFilter, BurialFilter, 'surname']
    inlines = [EventInline]
    search_fields = ['surname', 'forename', 'middle_names', 'maiden_name', 'notes']


class PhotographAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.base_fields['people'].widget = admin.widgets.FilteredSelectMultiple('people', False)
        super(PhotographAdminForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Photograph
        fields = '__all__'

class PhotographAdmin(admin.ModelAdmin):
    form = PhotographAdminForm
    list_display = ['__str__', 'caption']


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


class MarriageAdmin(admin.ModelAdmin):
    list_display = ['husband', 'wife', 'date', 'location', 'divorced']
    list_display_links = ['husband', 'wife']
    list_editable = ['date', 'location', 'divorced']
    search_fields = ['husband__surname', 'husband__forename', 'wife__maiden_name', 'wife__forename']


class LocationInline(admin.TabularInline):
    model = Location

class CountryAdmin(admin.ModelAdmin):
    list_display = ['name', 'country_code']
    inlines = [LocationInline]


class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'county_state_province', 'country', 'latitude', 'longitude']
    list_filter = ['country']
    search_fields = ['name', 'county_state_province', 'country__name']

admin.site = FamilyTreeAdminSite()
admin.site.register(Event, EventAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(Photograph, PhotographAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(Marriage, MarriageAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(Location, LocationAdmin)
