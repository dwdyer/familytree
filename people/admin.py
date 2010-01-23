from familytree.people.models import Person
from django.contrib import admin

class PersonAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'gender', 'date_of_birth']
    list_filter = ['gender']

admin.site.register(Person, PersonAdmin)
