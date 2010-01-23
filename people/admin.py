from familytree.people.models import Person, Marriage
from django.contrib import admin

class PersonAdmin(admin.ModelAdmin):
    list_display = ['name', 'gender', 'date_of_birth']
    list_filter = ['gender']
admin.site.register(Person, PersonAdmin)

admin.site.register(Marriage)
