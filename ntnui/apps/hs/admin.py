from django.contrib import admin

from .models import MainBoard, MainBoardMembership


class MainBoardMembershipInline(admin.TabularInline):
    model = MainBoardMembership


class MainBoardAdmin(admin.ModelAdmin):
    inlines = [MainBoardMembershipInline]


admin.site.register(MainBoard, MainBoardAdmin)
