from django.contrib import admin
from .models import Voter
# Register your models here.


class VoterAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['pid', 'birth']}),
        ('Photo', {'fields': ['image']})
    ]
    list_display = ('pid', 'birth', 'voted')
    search_fields = ['pid']


admin.site.register(Voter, VoterAdmin)
