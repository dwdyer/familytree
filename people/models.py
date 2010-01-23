from django.db import models

class Person(models.Model):
    name = models.CharField(max_length=50)
    gender = models.CharField(max_length=1, choices=(('M', 'Male'), ('F', 'Female')))
    date_of_birth = models.DateField()
    date_of_death = models.DateField(blank=True, null=True, default=None)
    mother = models.ForeignKey('self', blank=True, null=True, related_name='mother_of')
    father = models.ForeignKey('self', blank=True, null=True, limit_choices_to = {'gender': 'M'}, related_name='father_of')

    def __unicode__(self):
        return self.name
