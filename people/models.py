from datetime import date
from django.db import models
from django.db.models import Q
from familytree.people.relations import describe_relative
from sets import Set

class Person(models.Model):
    '''The main class of the model.  Every individual is represented by a person record.'''
    forename = models.CharField(max_length=20)
    middle_names = models.CharField(blank=True, max_length=50)
    surname = models.CharField(max_length=30)
    maiden_name = models.CharField(blank=True, max_length=30) # Maiden name is optional.
    gender = models.CharField(max_length=1, choices=(('M', 'Male'), ('F', 'Female')))
    date_of_birth = models.DateField()
    date_of_death = models.DateField(blank=True, null=True) # Date of death is blank for living people.
    mother = models.ForeignKey('self', blank=True, null=True, limit_choices_to = {'gender': 'F'}, related_name='mother_of')
    father = models.ForeignKey('self', blank=True, null=True, limit_choices_to = {'gender': 'M'}, related_name='father_of')

    def name(self, use_middle_names=True, use_maiden_name=False):
        '''Returns the full name of this person.'''
        name = " ".join([self.forename, self.middle_names]) if use_middle_names and self.middle_names else self.forename
        if self.maiden_name != "":
            return name + " " + (self.maiden_name if use_maiden_name else self.surname + u" (n\xe9e " + self.maiden_name + ")")
        else:
            return name + " " + self.surname

    def age(self):
        '''Calculate the person's age in years.'''
        end = self.date_of_death if self.is_deceased() else date.today()
        years = end.year - self.date_of_birth.year
        if end.month < self.date_of_birth.month or (end.month == self.date_of_birth.month and end.day < self.date_of_birth.day):
            years -= 1
        return years

    def is_deceased(self):
        return self.date_of_death != None

    def spouses(self):
        '''Return a list of anybody that this person is or was married to.'''
        if self.gender == 'F':
            return [m.husband for m in Marriage.objects.filter(wife=self).order_by('wedding_date')]
        else:
            return [m.wife for m in Marriage.objects.filter(husband=self).order_by('wedding_date')]

    def siblings(self):
        '''Returns a list of this person's brothers and sisters, including half-siblings.'''
        return Person.objects.filter(~Q(id=self.id), Q(~Q(father=None), father=self.father)|Q(~Q(mother=None), mother=self.mother)).order_by('date_of_birth')

    def children(self):
        '''Returns a list of this person's children.'''
        if self.gender == 'F':
            return Person.objects.filter(mother=self).order_by('date_of_birth')
        else:
            return Person.objects.filter(father=self).order_by('date_of_birth')

    def descendants(self):
        '''Returns a list of this person's descendants (their children and all of their children's descendents).'''
        descendants = []
        children = self.children()
        descendants += children
        for child in children:
            descendants += child.descendants()
        annotated_descendants = {}
        for descendant in descendants:
            annotated_descendants[descendant] = describe_relative(self, descendant)
        return annotated_descendants

    # Returns a dictionary of this person's ancestors.  The ancestors are the keys and each value is the distance (number of generations) from
    # this person to that ancestor (e.g parent is 1, grandparent is 2, etc.)
    def ancestor_distances(self, offset=0):
        '''Returns a dictionary of this person's ancestors (their parents and all of their parents's ancestors) with distance to each ancestor.'''
        ancestors = {} 
        if self.mother:
            ancestors[self.mother] = offset + 1
            ancestors.update(self.mother.ancestor_distances(offset + 1))
        if self.father:
            ancestors[self.father] = offset + 1
            ancestors.update(self.father.ancestor_distances(offset + 1))
        return ancestors

    def ancestors(self):
        '''Returns a list of this person's ancestors (their parents and all of their parent's ancestors).'''
        ancestors = self.ancestor_distances().keys()
        annotated_ancestors = {}
        for ancestor in ancestors:
            annotated_ancestors[ancestor] = describe_relative(self, ancestor)
        return annotated_ancestors

    def relatives(self):
        '''Returns a map of all of this person's blood relatives.  The keys are the relatives and the values describe the relationship.'''
        # Two people are related by blood if they share a common ancestor.
        ancestors = self.ancestors()
        # For efficiency, only consider root ancestors since their descendants' blood relatives will be a
        # subset of theirs and don't need to be considered separately.
        root_ancestors = filter(lambda a : not (a.father and a.mother), ancestors.keys()) if ancestors else [self]
        relatives = Set(root_ancestors)
        for ancestor in root_ancestors:
            relatives.update(ancestor.descendants().keys())
        relatives.remove(self) # This person can't be their own relative.
        annotated_relatives = {}
        for relative in relatives:
            annotated_relatives[relative] = describe_relative(self, relative)
        return annotated_relatives

    def __unicode__(self):
        return self.name()


class Marriage(models.Model):
    '''The marriage record links spouses.'''
    husband = models.ForeignKey(Person, limit_choices_to = {'gender': 'M'}, related_name='wife_of')
    wife = models.ForeignKey(Person, limit_choices_to = {'gender': 'F'}, related_name='husband_of')
    wedding_date = models.DateField()
    divorce_date = models.DateField(blank=True, null=True)

    def __unicode__(self):
        return self.husband.name(False) + ' & ' + self.wife.name(False, True)

