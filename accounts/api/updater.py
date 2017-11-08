from django.conf import settings
from .exeline import Exeline
from .formatter import ApiFormatter
from .filterer import ApiFilterer
from ..models import User, Contract


class Updater(object):

    def format_and_add_to_db(self, unformatted_members):
        members = ApiFormatter().format_response_list(unformatted_members)
        ntnui_members = ApiFilterer().filter_only_ntnui_members(members)

        for i, member in enumerate(ntnui_members):
            self.add_or_update_user_to_db(member, i, len(ntnui_members))

        return len(ntnui_members)

    def add_all_users_from_exeline(self):
        exeline = Exeline(settings.EXELINE_USER, settings.EXELINE_PASSWORD)
        gyms = exeline.get_members_for_all_gyms()
        all_members = gyms['1'] + gyms['2'] + gyms['3']
        return self.format_and_add_to_db(all_members)

    def add_last_day_users_from_exeline(self):
        exeline = Exeline(settings.EXELINE_USER, settings.EXELINE_PASSWORD)
        gyms = exeline.get_members_for_all_gyms_since(1)
        last_day_members = gyms['1'] + gyms['2'] + gyms['3']
        return self.format_and_add_to_db(last_day_members)

    def add_or_update_user_to_db(self, member, nr, total):
        user = None
        customer_number = member['customer_number'] or None
        print('(%i/%i) Updating or creating user with email %s (%s)' %
              (nr, total, member['email'], customer_number))
        user, user_created = User.objects.update_or_create(
            customer_number=customer_number,
            defaults={
                'customer_number': member['customer_number'],
                'email': member['email'],
                'first_name': member['first_name'],
                'last_name': member['last_name'],
                'is_active': member['active'],
                'phone': member['mobile'],
                'date_joined': member['registered_date']
            }
        )
        contract = member['contract']
        c, contract_created = Contract.objects.update_or_create(
            contract_number=contract['contract_number'],
            defaults={
                'person': user,
                'contract_number': contract['contract_number'],
                'contract_type': contract['type'],
                'start_date': contract['start_date'],
                'expiry_date': contract['expiry_date']
            }
        )
