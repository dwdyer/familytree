from django.db import models

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

    def is_deceased():
        return date_of_death != None

    def full_name(self):
        '''Returns the full name of this person (with maiden name in brackets if necessary)'''
        name = self.forename + " "
        if self.middle_names != "":
            name += self.middle_names + " "
        name += self.surname
        if self.maiden_name != "":
            name += u" (n\xe9e " + self.maiden_name + ")"
        return name

    def __unicode__(self):
        return self.full_name()
