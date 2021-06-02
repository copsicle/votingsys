from django.contrib import admin
from .models import Party
# Register your models here.


class PartyAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['letters']}),
        ('Note image', {'fields': ['note']})
    ]
    list_display = ('letters', 'count')
    search_fields = ['letters']


admin.site.register(Party, PartyAdmin)
