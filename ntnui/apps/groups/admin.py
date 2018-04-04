from django.contrib import admin

from .models import SportsGroup, Board, Membership, Invitation


class BoardInline(admin.StackedInline):
    model = Board
    extra = 1


class MembershipInline(admin.TabularInline):
    model = Membership
    extra = 1


class InvitationInline(admin.TabularInline):
    model = Invitation
    extra = 1
    readonly_fields = ('date_issued',)


class GroupAdmin(admin.ModelAdmin):
    inlines = [BoardInline, MembershipInline, InvitationInline]


admin.site.register(SportsGroup, GroupAdmin)
