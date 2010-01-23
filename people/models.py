from django.db import models
from django.db.models import Q

class Person(models.Model):
    forename = models.CharField(max_length=20)
    middle_names = models.CharField(blank=True, max_length=50)
    surname = models.CharField(max_length=30)
    maiden_name = models.CharField(blank=True, max_length=30)
    gender = models.CharField(max_length=1, choices=(('M', 'Male'), ('F', 'Female')))
    date_of_birth = models.DateField()
    date_of_death = models.DateField(blank=True, null=True)
    mother = models.ForeignKey('self', blank=True, null=True, limit_choices_to = {'gender': 'F'}, related_name='mother_of')
    father = models.ForeignKey('self', blank=True, null=True, limit_choices_to = {'gender': 'M'}, related_name='father_of')

    def full_name(self):
        '''Returns the full name of this person (with maiden name in brackets if necessary)'''
        name = self.forename + " "
        if self.middle_names != "":
            name += self.middle_names + " "
        name += self.surname
        if self.maiden_name != "":
            name += u" (n\xe9e " + self.maiden_name + ")"
        return name

    def is_deceased(self):
        return self.date_of_death != None

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
        return self.full_name()
