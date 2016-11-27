from django.contrib import admin
from django.db.models import Q
from people.models import Event

class HasEventFilter(admin.SimpleListFilter):
    '''Convenient base class for filters that test for the existence of
    different event types. Do not instantiate this class directly, use one of
    the sub-classes below.'''

    event_type = None

    def lookups(self, request, model_admin):
        return [('yes', 'Yes'), ('no', 'No')]

    def queryset(self, request, queryset):
        filter_option = self.value()
        if filter_option == 'yes':
            return queryset.filter(events__event_type=self.event_type)
        elif filter_option == 'no':
            return queryset.exclude(events__event_type=self.event_type)
        else:
            return queryset


class BirthFilter(HasEventFilter):
    event_type = Event.BIRTH
    title = 'has birth record'
    parameter_name = 'birth'


class BaptismFilter(HasEventFilter):
    event_type = Event.BAPTISM
    title = 'has baptism record'
    parameter_name = 'baptism'


class DeathFilter(HasEventFilter):
    event_type = Event.DEATH
    title = 'has death record'
    parameter_name = 'death'


class BurialFilter(HasEventFilter):
    event_type = Event.BURIAL
    title = 'has burial record'
    parameter_name = 'burial'


class HasReferenceFilter(admin.SimpleListFilter):
    title = 'has reference'
    parameter_name = 'has_url'

    def lookups(self, request, model_admin):
        return [('yes', 'Yes'), ('no', 'No')]

    def queryset(self, request, queryset):
        filter_option = self.value()
        if filter_option == 'yes':
            return queryset.exclude(Q(reference__isnull=True) | Q(reference=''))
        elif filter_option == 'no':
            return queryset.filter(Q(reference__isnull=True) | Q(reference=''))
        else:
            return queryset
