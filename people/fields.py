from django import forms
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import dateformat
import datetime

class UncertainDate(object):
    '''An uncertain date must specify at least a year but doesn't have to
    specify the month or day.'''

    def __init__(self, year, month=None, day=None):
        if day and not month:
            raise ValueError('Cannot specify day without month.')
        elif day:
            self.lower_bound = datetime.date(year, month, day)
        elif month:
            self.lower_bound = datetime.date(year, month, 1)
        else:
            self.lower_bound = datetime.date(year, 1, 1)
        self.year = year
        self.month = month
        self.day = day

    def __repr__(self):
        if self.day:
            return '{0:04d}-{1:02d}-{2:02d}'.format(self.year, self.month, self.day)
        elif self.month:
            return '{0:04d}-{1:02d}'.format(self.year, self.month)
        else:
            return repr(self.year)

    def __str__(self):
        if self.day:
            return dateformat.format(self.lower_bound, 'l jS F Y')
        elif self.month:
            return dateformat.format(self.lower_bound, 'F Y')
        else:
            return dateformat.format(self.lower_bound, 'Y')

    def __lt__(self, other):
        return self.lower_bound < other.lower_bound

    def __len__(self):
        return len(repr(self))

    def short(self):
        if self.day:
            return dateformat.format(self.lower_bound, 'jS F Y')
        elif self.month:
            return dateformat.format(self.lower_bound, 'F Y')
        else:
            return dateformat.format(self.lower_bound, 'Y')


class UncertainDateField(models.Field):
    '''Stores a possibly incomplete date as a (partial) ISO format date
    (i.e. YYYY-MM-DD, YYYY-MM or YYYY).'''

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 10
        super(UncertainDateField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(UncertainDateField, self).deconstruct()
        del kwargs['max_length']
        return name, path, args, kwargs

    def from_db_value(self, value, expression, connection, context):
       return _parse_date_string(value)

    def to_python(self, value):
        if isinstance(value, UncertainDate):
            return value
        else:
            return _parse_date_string(value)


    def get_db_prep_value(self, value, connection, prepared=False):
        return None if value in ('', None) else repr(value)

    def get_prep_lookup(self, lookup_type, value):
        if lookup_type in ('gt', 'gte', 'lt', 'lte'):
            return self.get_db_prep_value(value)
        else:
            raise TypeError('Lookup type %r not supported' % lookup_type)

    def formfield(self, **kwargs):
        defaults = {'form_class': UncertainDateFormField}
        defaults.update(kwargs)
        return super(UncertainDateField, self).formfield(**defaults)

    def get_internal_type(self):
        return 'CharField'


class UncertainDateFormField(forms.CharField):

    def __init__(self, *args, **kwargs):
        super(UncertainDateFormField, self).__init__(max_length=10, min_length=4, *args, **kwargs)

    def to_python(self, value):
        if isinstance(value, UncertainDate):
            return value
        else:
            return _parse_date_string(value)

    def prepare_value(self, value):
        return repr(value) if isinstance(value, UncertainDate) else value


def _parse_date_string(string):
    if string in ('', None, 'None'):
        return None
    else:
        fields = string.split('-')
        try:
            if len(fields) == 3:
                return UncertainDate(int(fields[0]), int(fields[1]), int(fields[2]))
            elif len(fields) == 2:
                return UncertainDate(int(fields[0]), int(fields[1]))
            else:
                return UncertainDate(int(fields[0]))
        except ValueError:
            raise ValidationError('Invalid date string.')
