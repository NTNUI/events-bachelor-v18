from django.contrib import admin

from .models import SportsGroup, Board, Membership, Invitation


class BoardInline(admin.StackedInline):
    model = Board


class MembershipInline(admin.TabularInline):
    model = Membership


class InvitationInline(admin.TabularInline):
    model = Invitation
    readonly_fields = ('date_issued',)


class GroupAdmin(admin.ModelAdmin):
    inlines = [BoardInline, MembershipInline, InvitationInline]


admin.site.register(SportsGroup, GroupAdmin)
