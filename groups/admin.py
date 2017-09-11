from django.contrib import admin

from .models import SportsGroup, Board, Membership

class BoardInline(admin.StackedInline):
    model = Board

class MembershipInline(admin.TabularInline):
    model = Membership

class GroupAdmin(admin.ModelAdmin):
    inlines = [BoardInline, MembershipInline]

admin.site.register(SportsGroup, GroupAdmin)
