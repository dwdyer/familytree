from people.models import Person, Marriage, Photograph
from django.contrib import admin

class PersonAdmin(admin.ModelAdmin):
    list_display = ['surname', 'name', 'gender', 'date_of_birth', 'deceased']
    list_filter = ['gender', 'deceased', 'surname']
admin.site.register(Person, PersonAdmin)

class PhotographAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'caption']
admin.site.register(Photograph, PhotographAdmin)

admin.site.register(Marriage)
