from datetime import date
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from opencage.geocoder import OpenCageGeocode
from people.fields import UncertainDateField
from people.relations import closest_common_ancestor, describe_relative
from sets import Set
from taggit.managers import TaggableManager
from tinymce.models import HTMLField
import os
import settings

class Country(models.Model):
    name = models.CharField(max_length=50)
    country_code = models.CharField(max_length=3)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'countries'


class Location(models.Model):
    '''A location is not meant to be a pinpoint address but a general place such
    as a town or village.'''
    name = models.CharField(max_length=50)
    county_state_province = models.CharField(max_length=30)
    country = models.ForeignKey(Country)
    # If left blank, these fields will be set by geocoding when the model is
    # saved.
    longitude = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not (self.longitude and self.latitude):
            try:
                geocoder = OpenCageGeocode(settings.OPENCAGE_API_KEY)
                query = '{0}, {1}, {2}'.format(self.name,
                                               self.county_state_province,
                                               self.country.name)
                result = geocoder.geocode(query)
                geometry = result[0].get('geometry')
                self.latitude = geometry.get('lat')
                self.longitude = geometry.get('lng')
            except e:
                # If something goes wrong, there's not much we can do, just leave
                # the coordinates blank.
                print e
        super(Location, self).save(*args, **kwargs)

    def __unicode__(self):
        return '{0}, {1}'.format(self.name, self.county_state_province)

    class Meta:
        ordering = ['country', 'county_state_province', 'name']


class Person(models.Model):
    '''The main class of the model. Every individual is represented by a person
    record.'''
    forename = models.CharField(max_length=20)
    middle_names = models.CharField(blank=True, max_length=50)
    surname = models.CharField(max_length=30)
    maiden_name = models.CharField(blank=True, max_length=30) # Maiden name is optional.
    gender = models.CharField(max_length=1, choices=(('M', 'Male'), ('F', 'Female')))
    date_of_birth = UncertainDateField(blank=True, null=True)
    birth_location = models.ForeignKey(Location, blank=True, null=True, related_name='natives')
    date_of_death = UncertainDateField(blank=True, null=True)
    deceased = models.BooleanField(default=True)
    mother = models.ForeignKey('self', blank=True, null=True, limit_choices_to={'gender': 'F'}, related_name='children_of_mother')
    father = models.ForeignKey('self', blank=True, null=True, limit_choices_to={'gender': 'M'}, related_name='children_of_father')
    notes = HTMLField(blank=True)
    tags = TaggableManager(blank=True)

    def name(self, use_middle_names=True, use_maiden_name=False):
        '''Returns the full name of this person.'''
        name = " ".join([self.forename, self.middle_names]) if use_middle_names and self.middle_names else self.forename
        if self.maiden_name != "":
            return name + " " + (self.maiden_name if use_maiden_name else self.surname + u" (n\xe9e " + self.maiden_name + ")")
        else:
            return name + " " + self.surname

    def age(self):
        '''Calculate the person's age in years.'''
        if not self.date_of_birth or (self.deceased and not self.date_of_death):
            return None
        end = self.date_of_death if self.deceased else date.today()
        years = end.year - self.date_of_birth.year
        if end.month < self.date_of_birth.month or (end.month == self.date_of_birth.month and end.day < self.date_of_birth.day):
            years -= 1
        return years

    def year_range(self):
        if self.date_of_birth:
            return '{0}-{1}'.format(self.date_of_birth.year,
                                    '' if not self.deceased else self.date_of_death.year if self.date_of_death else '????')
        else:
            return ''

    def spouses(self):
        '''Return a list of anybody that this person is or was married to.'''
        if self.gender == 'F':
            return [m.husband for m in self.husband_of.all()]
        else:
            return [m.wife for m in self.wife_of.all()]

    def siblings(self):
        '''Returns a list of this person's brothers and sisters, including
        half-siblings.'''
        return Person.objects.filter(~Q(id=self.id),
                                     Q(~Q(father=None), father=self.father) | Q(~Q(mother=None), mother=self.mother)).order_by('date_of_birth')

    def children(self):
        '''Returns a list of this person's children.'''
        offspring = self.children_of_mother if self.gender == 'F' else self.children_of_father
        return offspring.order_by('date_of_birth')

    def _descendant_distances(self, offset=0):
        descendants = {}
        for child in self.children():
            descendants[child] = offset + 1
            descendants.update(child._descendant_distances(offset + 1))
        return descendants

    def descendants(self):
        '''Returns a list of this person's descendants (their children and all
        of their children's descendents).'''
        descendants = []
        children = self.children()
        descendants += children
        for child in children:
            descendants += child.descendants()
        return descendants

    def annotated_descendants(self):
        '''Returns a list of this person's descendants annotated with the name
        of the relationship to this person (so a list of (Person, relationship)
        tuples.'''
        distances = self._descendant_distances()
        descendants = []
        for descendant in distances.keys():
            descendants.append((descendant, describe_relative(self, descendant), distances[descendant]))
        descendants.sort(key=lambda (p, r, d): (d, r, p.surname))
        return descendants

    # Returns a dictionary of this person's ancestors.  The ancestors are the
    # keys and each value is the distance (number of generations) from this
    # person to that ancestor (e.g parent is 1, grandparent is 2, etc.)
    def _ancestor_distances(self, offset=0):
        '''Returns a dictionary of this person's ancestors (their parents and
        all of their parents's ancestors) with distance to each ancestor.'''
        ancestors = {}
        if self.mother:
            ancestors[self.mother] = offset + 1
            ancestors.update(self.mother._ancestor_distances(offset + 1))
        if self.father:
            ancestors[self.father] = offset + 1
            ancestors.update(self.father._ancestor_distances(offset + 1))
        return ancestors

    def ancestors(self):
        '''Returns a list of this person's ancestors (their parents and all of
        their parent's ancestors).'''
        return self._ancestor_distances().keys()

    def annotated_ancestors(self):
        '''Returns a list of this person's ancestors annotated with the name of
        the relationship to this person (so a list of (Person, relationship)
        tuples.'''
        distances = self._ancestor_distances()
        ancestors = []
        for ancestor in distances.keys():
            ancestors.append((ancestor, describe_relative(self, ancestor), distances[ancestor]))
        ancestors.sort(key=lambda (p, r, d): (d, r, p.surname))
        return ancestors

    def relatives(self):
        '''Returns a list of all of this person's blood relatives. The first
        item in each tuple is the person and the second is the relationship.'''
        # Two people are related by blood if they share a common ancestor.
        ancestor_distances = self._ancestor_distances()
        # For efficiency, only consider root ancestors since their
        # descendants' blood relatives will be a subset of theirs and don't need
        # to be considered separately.
        root_ancestors = [p for p in ancestor_distances.keys() if not (p.father and p.mother)] or [self]
        relatives = Set(root_ancestors)
        for ancestor in root_ancestors:
            relatives.update(ancestor.descendants())
        relatives.remove(self) # This person can't be their own relative.
        distances = ancestor_distances.copy()
        distances.update(self._descendant_distances())
        annotated = []
        for relative in relatives:
            distance = distances.get(relative, None)
            if not distance:
                (_, d1, d2) = closest_common_ancestor(ancestor_distances, relative._ancestor_distances())
                distance = max(d1, d2)
            annotated.append((relative, describe_relative(self, relative), distance))
        annotated.sort(key=lambda (p, r, d): (d, r, p.surname))
        return annotated

    def photos(self):
        '''Returns a list of all photos associated with this person.'''
        return Photograph.objects.filter(person=self)

    def clean(self):
        if self.date_of_death and not self.deceased:
            raise ValidationError('Cannot specify date of death for living person.')

    def __unicode__(self):
        return self.name()

    class Meta:
        ordering = ['surname', 'forename', 'middle_names', '-date_of_birth']


class Marriage(models.Model):
    '''The marriage record links spouses.'''
    husband = models.ForeignKey(Person, limit_choices_to={'gender': 'M'}, related_name='wife_of')
    wife = models.ForeignKey(Person, limit_choices_to={'gender': 'F'}, related_name='husband_of')
    wedding_date = UncertainDateField(blank=True, null=True)
    divorced = models.BooleanField(default=False)

    def __unicode__(self):
        return self.husband.name(False) + ' & ' + self.wife.name(False, True)


class Photograph(models.Model):
    '''The photograph record combines an image with an optional caption and date
    and links it to one or more people.'''
    image = models.ImageField(upload_to='photos', blank=False, null=False)
    people = models.ManyToManyField(Person, related_name='photos')
    caption = models.TextField(blank=True)
    date = models.DateField(blank=True, null=True)

    def __unicode__(self):
        return self.image.url

    class Meta:
        ordering = ['date']


class Document(models.Model):
    file = models.FileField(upload_to='documents', blank=False, null=False)
    title = models.CharField(max_length=100)
    people = models.ManyToManyField(Person, related_name='documents')

    def file_extension(self):
        _, extension = os.path.splitext(self.file.name)
        return extension[1:]

    def __unicode__(self):
        return self.title
