from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from people.filters import BirthFilter, BaptismFilter, DeathFilter, BurialFilter, HasReferenceFilter
from people.models import Country, Location, Person, Marriage, Photograph, Document, Event, SurnameVariant

class FamilyTreeAdminSite(admin.AdminSite):
    def each_context(self, request):
        context = super(FamilyTreeAdminSite, self).each_context(request)
        context['list'] = Person.objects.select_related('birth')
        return context


class EventAdmin(admin.ModelAdmin):
    list_display = ['event_date', 'event_type', 'person', 'location']
    list_filter = ['event_type', HasReferenceFilter]

    def event_date(self, obj):
        return obj.date.short()
    event_date.admin_order_field = 'date'


class EventInline(admin.TabularInline):
    model = Event
    extra = 1

class PersonAdmin(admin.ModelAdmin):
    fieldsets = [(None, {'fields': [('forename', 'middle_names', 'known_as'),
                                    ('surname', 'maiden_name'),
                                    ('gender', 'blood_relative', 'deceased'),
                                    ('mother', 'father'),
                                    'notes',
                                    ('tags', 'user')]})]
    list_display = ['full_name', 'gender', 'born', 'birth_location']
    list_display_links = ['full_name']
    list_filter = ['blood_relative', BirthFilter, BaptismFilter, DeathFilter, BurialFilter,
                   'surname', 'gender', 'deceased']
    inlines = [EventInline]
    search_fields = ['surname', 'forename', 'middle_names', 'known_as', 'maiden_name', 'notes']

    def born(self, obj):
        return obj.date_of_birth().short() if obj.date_of_birth() else None

    def full_name(self, obj):
        return obj.name()
    full_name.admin_order_field = 'surname'


class PhotographAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.base_fields['people'].widget = admin.widgets.FilteredSelectMultiple('people', False)
        super(PhotographAdminForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Photograph
        fields = '__all__'

class PhotographAdmin(admin.ModelAdmin):
    form = PhotographAdminForm
    list_display = ['__str__', 'caption', 'date']


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


class SurnameVariantAdmin(admin.ModelAdmin):
    list_display = ['canonical', 'variant']
    search_fields = ['canonical', 'variant']


admin.site = FamilyTreeAdminSite()

admin.site.register(Group, GroupAdmin)
admin.site.register(User, UserAdmin)

admin.site.register(Event, EventAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(Photograph, PhotographAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(Marriage, MarriageAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(SurnameVariant, SurnameVariantAdmin)
