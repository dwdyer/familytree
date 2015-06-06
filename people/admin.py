from people.models import Country, Location, Person, Marriage, Photograph
from django.contrib import admin

class PersonAdmin(admin.ModelAdmin):
    fieldsets = [(None, {'fields': [('forename', 'middle_names'),
                                    ('surname', 'maiden_name'),
                                    'gender',
                                    ('date_of_birth', 'birth_location'),
                                    ('deceased', 'date_of_death'),
                                    ('mother', 'father'),
                                    'notes',
                                    'tags']})]
    list_display = ['surname', 'name', 'gender', 'date_of_birth', 'birth_location', 'deceased']
    list_display_links = ['name']
    list_editable = ['date_of_birth', 'birth_location']
    list_filter = ['gender', 'deceased', 'surname']
admin.site.register(Person, PersonAdmin)


class PhotographAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'caption']
admin.site.register(Photograph, PhotographAdmin)


class MarriageAdmin(admin.ModelAdmin):
    list_display = ['husband', 'wife', 'wedding_date']
admin.site.register(Marriage, MarriageAdmin)


class LocationInline(admin.TabularInline):
    model = Location

class CountryAdmin(admin.ModelAdmin):
    list_display = ['name', 'country_code']
    inlines = [LocationInline]
admin.site.register(Country, CountryAdmin)


class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'county_state_province', 'country']
admin.site.register(Location, LocationAdmin)
