from django.contrib import admin
from .models import User, Contract


class ContractInline(admin.TabularInline):
    model = Contract


class UserAdmin(admin.ModelAdmin):
    inlines = [ContractInline]
    search_fields = ['last_name', 'first_name']
    exclude = ('groups', 'user_permissions')

    def get_list_display(self, request):
        return ('customer_number', 'first_name',
                'last_name', 'email', 'phone',
                'date_joined', 'number_of_contracts')


class ContractAdmin(admin.ModelAdmin):
    search_fields = ['contract_number']

    def get_list_display(self, request):
        return ('contract_number', 'person', 'contract_type',
                'start_date', 'expiry_date')


admin.site.register(Contract, ContractAdmin)
admin.site.register(User, UserAdmin)
