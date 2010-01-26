from familytree.people.models import Person, Marriage, Photograph
from django.contrib import admin

class PersonAdmin(admin.ModelAdmin):
    list_display = ['name', 'gender', 'date_of_birth']
    list_filter = ['gender']
admin.site.register(Person, PersonAdmin)

class PhotographAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'caption']
admin.site.register(Photograph, PhotographAdmin)

admin.site.register(Marriage)
