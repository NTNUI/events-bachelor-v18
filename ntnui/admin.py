from django.contrib import admin

from accounts.models import User


class UserAdmin(admin.ModelAdmin):
    search_fields = ['last_name', 'first_name']
    exclude = ('groups','user_permissions')

    def get_list_display(self, request):
        return ('customer_no','first_name','last_name', 'email', 'phone', 'date_joined')


admin.site.register(User, UserAdmin)
