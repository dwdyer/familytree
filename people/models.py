from datetime import date
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Count, Q
from django.db.models.signals import post_delete
from django.dispatch.dispatcher import receiver
from itertools import chain
from opencage.geocoder import OpenCageGeocode
from operator import attrgetter
from people.fields import UncertainDateField
from people.relations import closest_common_ancestor, describe_relative
from taggit.managers import TaggableManager
from taggit.models import Tag, TaggedItem
from tinymce.models import HTMLField
import os
import settings

class Country(models.Model):
    name = models.CharField(max_length=50)
    country_code = models.CharField(max_length=3)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'countries'


class Location(models.Model):
    '''A location is not meant to be a pinpoint address but a general place such
    as a town or village.'''
    name = models.CharField(max_length=50, help_text='Place name')
    county_state_province = models.CharField(max_length=30,
                                             verbose_name='county/state/province',
                                             help_text='County / state / province')
    country = models.ForeignKey(Country, help_text='Country')
    # If left blank, these fields will be set by geocoding when the model is
    # saved.
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not (self.latitude and self.longitude):
            try:
                geocoder = OpenCageGeocode(settings.OPENCAGE_API_KEY)
                query = '{0}, {1}, {2}'.format(self.name,
                                               self.county_state_province,
                                               self.country.name)
                result = geocoder.geocode(query)
                geometry = result[0].get('geometry')
                self.latitude = geometry.get('lat')
                self.longitude = geometry.get('lng')
            except Exception as e:
                # If something goes wrong, there's not much we can do, just leave
                # the coordinates blank.
                print (e)
        super(Location, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('location', args=[self.id])

    def __str__(self):
        return '{0}, {1}'.format(self.name, self.county_state_province)

    def __eq__(self, other):
        if other:
            return self.name == other.name and self.latitude == other.latitude and self.longitude == other.longitude
        else:
            return False

    def __hash__(self):
        return hash(self.name) + hash(self.latitude) + hash(self.longitude)

    class Meta:
        ordering = ['country', 'county_state_province', 'name']
        unique_together = [('country', 'county_state_province', 'name')]


class Person(models.Model):
    '''The main class of the model. Every individual is represented by a person
    record.'''
    forename = models.CharField(max_length=20, help_text='Forename / given name')
    middle_names = models.CharField(blank=True, max_length=50, help_text='Middle names(s)')
    known_as = models.CharField(blank=True, max_length=20, help_text='Known as')
    surname = models.CharField(max_length=30, help_text='Surname')
    maiden_name = models.CharField(blank=True, max_length=30, help_text='Maiden name') # Maiden name is optional.
    gender = models.CharField(max_length=1,
                              choices=(('M', 'Male'), ('F', 'Female')),
                              blank=False,
                              default=None)
    birth = models.ForeignKey('Event', models.SET_NULL, null=True, blank=True, related_name='+')
    death = models.ForeignKey('Event', models.SET_NULL, null=True, blank=True, related_name='+')
    deceased = models.BooleanField(default=True)
    blood_relative = models.BooleanField(default=True)
    mother = models.ForeignKey('self',
                               blank=True,
                               null=True,
                               limit_choices_to={'gender': 'F'},
                               related_name='children_of_mother',
                               on_delete=models.SET_NULL)
    father = models.ForeignKey('self',
                               blank=True,
                               null=True,
                               limit_choices_to={'gender': 'M'},
                               related_name='children_of_father',
                               on_delete=models.SET_NULL)
    notes = HTMLField(blank=True)
    tags = TaggableManager(blank=True, help_text='Tags')
    # A person can be linked to a user account. This allows a user to see
    # information relevant to their own relationships.
    user = models.OneToOneField(User, blank=True, null=True)

    def name(self, use_middle_names=True, use_maiden_name=False):
        '''Returns the full name of this person.'''
        name = ' '.join([self.forename, self.middle_names]) if use_middle_names and self.middle_names else self.forename
        if self.known_as:
            name = name + ' "{0}"'.format(self.known_as)
        if self.maiden_name != '':
            return name + ' ' + (self.maiden_name if use_maiden_name else self.surname.upper() + u' (n\xe9e ' + self.maiden_name + ')')
        else:
            return name + ' ' + self.surname.upper()

    def given_names(self):
        return " ".join([self.forename, self.middle_names]) if self.middle_names else self.forename

    def birth_surname(self):
        return self.maiden_name if self.maiden_name else self.surname

    def birth_name(self):
        return '{0} {1}'.format(self.given_names(), self.birth_surname().upper())

    def date_of_birth(self):
        return self.birth.date if self.birth else None

    def birth_location(self):
        return self.birth.location if self.birth else None

    def date_of_death(self):
        return self.death.date if self.death else None

    def age(self):
        '''Calculate the person's age in years.'''
        if not self.date_of_birth() or (self.deceased and not self.date_of_death()):
            return None
        end = self.date_of_death() if self.deceased else date.today()
        years = end.year - self.date_of_birth().year
        if end.month and self.date_of_birth().month:
            if end.month < self.date_of_birth().month \
               or (end.month == self.date_of_birth().month \
                   and end.day and self.date_of_birth().day and end.day < self.date_of_birth().day):
                years -= 1
        return years

    def year_range(self):
        return '{0}-{1}'.format(self.date_of_birth().year if self.date_of_birth() else '????',
                                '' if not self.deceased else self.date_of_death().year if self.date_of_death() else '????')

    def spouses(self):
        '''Return a list of anybody that this person is or was married to.'''
        if self.gender == 'F':
            return [(m.husband, m.date, m.location, m.divorced) for m in self.wife_of.all()]
        else:
            return [(m.wife, m.date, m.location, m.divorced) for m in self.husband_of.all()]

    def siblings(self):
        '''Returns a list of this person's brothers and sisters, including
        half-siblings.'''
        return Person.objects.filter(~Q(id=self.id),
                                     Q(~Q(father=None), father=self.father) | \
                                     Q(~Q(mother=None), mother=self.mother)).order_by('birth__date')

    def children(self):
        '''Returns a list of this person's children.'''
        offspring = self.children_of_mother if self.gender == 'F' else self.children_of_father
        return offspring.select_related('birth', 'death').order_by('birth__date')

    def marriages(self):
        return self.husband_of.all() if self.gender == 'M' else self.wife_of.all()

    def timeline(self):
        timeline = list(self.events.all()) + list(self.marriages().filter(date__isnull=False))
        timeline.sort(key=attrgetter('date'))
        timeline.sort(key=attrgetter('event_type'))
        return timeline

    def _descendant_distances(self, offset=0):
        descendants = {}
        for child in self.children():
            descendants[child] = offset + 1
            descendants.update(child._descendant_distances(offset + 1))
        return descendants

    def descendants(self):
        '''Returns a list of this person's descendants (their children and all
        of their children's descendants).'''
        for child in self.children():
            yield child
            yield from child.descendants()

    def annotated_descendants(self):
        '''Returns a list of this person's descendants annotated with the name
        of the relationship to this person (so a list of (Person, relationship)
        tuples.'''
        distances = self._descendant_distances()
        descendants = []
        for descendant in distances.keys():
            relationship = describe_relative(self, descendant, {}, descendant._ancestor_distances())
            descendants.append((descendant, relationship, distances[descendant]))
        descendants.sort(key=lambda x: (x[2], x[1], x[0].surname))
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
        their parents' ancestors).'''
        if self.mother:
            yield self.mother
            yield from self.mother.ancestors()
        if self.father:
            yield self.father
            yield from self.father.ancestors()

    def annotated_ancestors(self):
        '''Returns a list of this person's ancestors annotated with the name of
        the relationship to this person and the distance between them (so a list
        of (Person, relationship, distance) tuples).'''
        distances = self._ancestor_distances()
        ancestors = []
        for ancestor in distances.keys():
            relationship = describe_relative(self, ancestor, distances, {})
            ancestors.append((ancestor, relationship, distances[ancestor]))
        ancestors.sort(key=lambda x: (x[2], x[1], x[0].surname))
        return ancestors

    def relatives(self):
        relatives = self._build_relatives_set(set())
        relatives.discard(self) # This person can't be their own relative.
        return relatives

    def _build_relatives_set(self, relatives_set):
        '''Adds all blood relatives of this person to the specified set.'''
        relatives_set.add(self)
        for child in self.children():
            if child not in relatives_set:
                relatives_set.add(child)
                relatives_set.update(child.descendants())
        if self.father:
            self.father._build_relatives_set(relatives_set)
        if self.mother:
            self.mother._build_relatives_set(relatives_set)
        return relatives_set

    def annotated_relatives(self):
        '''Returns a list of all of this person's blood relatives. The first
        item in each tuple is the person, the second is the relationship, and
        the third is the distance between the two individuals.'''
        ancestor_distances = self._ancestor_distances()
        distances = ancestor_distances.copy()
        distances.update(self._descendant_distances())
        annotated = []
        for relative in self.relatives():
            distance = distances.get(relative, None)
            relative_distances = relative._ancestor_distances()
            if not distance:
                (_, d1, d2) = closest_common_ancestor(ancestor_distances, relative_distances)
                distance = max(d1, d2)
            relationship = describe_relative(self, relative, ancestor_distances, relative_distances)
            annotated.append((relative, relationship, distance))
        annotated.sort(key=lambda x: (x[2], x[1], x[0].surname))
        return annotated

    def photos(self):
        '''Returns a list of all photos associated with this person.'''
        return Photograph.objects.filter(person=self)

    def has_missing_maiden_name(self):
        return self.gender == 'F' and self.wife_of.count() > 0 and (self.maiden_name=='' or self.maiden_name==None)

    def clean(self):
        if self.date_of_death() and not self.deceased:
            raise ValidationError('Cannot specify date of death for living person.')
        if self.birth and self.birth.person.id != self.id:
            raise ValidationError('Birth event must refer back to the same person.')
        if self.death and self.death.person.id != self.id:
            raise ValidationError('Death event must refer back to the same person.')
        if (self.mother and self.mother == self) or (self.father and self.father == self):
            raise ValidationError('Person cannot be their own parent.')

    def get_absolute_url(self):
        return reverse('person', args=[self.id])

    def __str__(self):
        return self.name()

    class Meta:
        ordering = ['surname', 'forename', 'middle_names', '-birth__date']


class Event(models.Model):
    '''Arbitrary event connected to a person.'''
    BIRTH = 0
    BAPTISM = 1
    MARRIAGE = 2
    DEATH = 3
    BURIAL = 4
    EVENT_TYPE = [(BIRTH, 'Birth'),
                  (BAPTISM, 'Baptism'),
                  (DEATH, 'Death'),
                  (BURIAL, 'Burial')]

    person = models.ForeignKey(Person, related_name='events')
    event_type = models.PositiveSmallIntegerField(choices=EVENT_TYPE)
    date = UncertainDateField()
    location = models.ForeignKey(Location, blank=True, null=True, related_name='events')
    reference = models.URLField(blank=True, null=True)

    def verb(self):
        if self.event_type == Event.BIRTH:
            return 'born'
        elif self.event_type == Event.BAPTISM:
            return 'baptised'
        elif self.event_type == Event.MARRIAGE:
            return 'married'
        elif self.event_type == Event.DEATH:
            return 'died'
        elif self.event_type == Event.BURIAL:
            return 'buried'
        else:
            return None

    def save(self, *args, **kwargs):
        super(Event, self).save(*args, **kwargs)
        # If this event is a birth or death event, the corresponding person
        # record must point back to it for the database to be consistent, so
        # update that here.
        if self.event_type == Event.BIRTH:
            self.person.birth = self
            self.person.save()
        elif self.event_type == Event.DEATH:
            self.person.death = self
            self.person.save()

    class Meta:
        ordering = ['date']


class Marriage(models.Model):
    '''The marriage record links spouses.'''
    event_type = Event.MARRIAGE
    husband = models.ForeignKey(Person, limit_choices_to={'gender': 'M'}, related_name='husband_of')
    wife = models.ForeignKey(Person, limit_choices_to={'gender': 'F'}, related_name='wife_of')
    date = UncertainDateField(blank=True, null=True)
    location = models.ForeignKey(Location, blank=True, null=True, related_name='weddings')
    divorced = models.BooleanField(default=False)
    reference = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.husband.name(False) + ' & ' + self.wife.name(False, True)

    def verb(self):
        return 'married'

    class Meta:
        ordering = ['husband__surname', 'husband__forename', 'husband__middle_names', 'date']


class Photograph(models.Model):
    '''The photograph record combines an image with an optional caption and date
    and links it to one or more people.'''
    image = models.ImageField(upload_to='photos', blank=False, null=False)
    people = models.ManyToManyField(Person, related_name='photos')
    caption = models.TextField(blank=True)
    date = UncertainDateField(blank=True, null=True)
    location = models.ForeignKey(Location, blank=True, null=True, related_name='photos')

    def __str__(self):
        return self.image.url

    class Meta:
        ordering = ['-date']


class Document(models.Model):
    file = models.FileField(upload_to='documents', blank=False, null=False)
    title = models.CharField(max_length=100)
    people = models.ManyToManyField(Person, related_name='documents')

    def file_extension(self):
        _, extension = os.path.splitext(self.file.name)
        return extension[1:]

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']


class SurnameVariant(models.Model):
    '''Some surnames have changed spellings over time. This model links
    different versions of the same surname together.'''
    canonical = models.CharField(max_length=30, help_text='Canonical surname')
    variant = models.CharField(max_length=30, help_text='Surname variant')


# Delete tags that are no longer in use.
@receiver([post_delete], sender=TaggedItem)
def delete_unused_tags(sender, instance, **kwargs):
    for tag in Tag.objects.annotate(item_count=Count('taggit_taggeditem_items')).filter(item_count=0):
        tag.delete()
