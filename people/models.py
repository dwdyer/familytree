from django.db import models
from django.db.models import Q

class Person(models.Model):
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

    def __unicode__(self):
        return self.name()


class Marriage(models.Model):
    husband = models.ForeignKey(Person, limit_choices_to = {'gender': 'M'}, related_name='wife_of')
    wife = models.ForeignKey(Person, limit_choices_to = {'gender': 'F'}, related_name='husband_of')
    wedding_date = models.DateField()
    divorce_date = models.DateField(blank=True, null=True)

    def __unicode__(self):
        return self.husband.name(False) + ' & ' + self.wife.name(False, True)

