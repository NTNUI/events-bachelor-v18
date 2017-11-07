from django.contrib import admin

from .models import MainBoard, HSMembership

class HSMembershipInline(admin.TabularInline):
    model = HSMembership

class HSAdmin(admin.ModelAdmin):
    inlines = [ HSMembershipInline ]

admin.site.register(MainBoard, HSAdmin)
