
class ApiFormatter(object):

    def capital_first_letter(self, word):
        return word.title()

    def format_customer_response(self, unformatted):
        expected_attributes = [
            'CustomerNo',
            'GymID',
            'FirstName',
            'LastName',
            'BirthDate',
            'Mobile',
            'Email',
            'Gender',
            'Active',
            'ExpieryDate',
            'CardNumber',
            'RegisterdDate',
            'LastVisitDate',
            'CurrentOffering',
            'ContractNumber',
            'ContractStartdate',
        ]
        expected_keys = set(expected_attributes)
        present_keys = set(unformatted.keys())
        if not expected_keys.issubset(present_keys):
            missing_keys = expected_keys - present_keys
            raise Exception('Missing attributes in customer: %s' %
                            missing_keys)

        return {
            'customer_no': unformatted['CustomerNo'],
            'gym_id': unformatted['GymID'],
            'first_name': self.capital_first_letter(unformatted['FirstName']),
            'last_name': self.capital_first_letter(unformatted['LastName']),
            'birth_date': unformatted['BirthDate'],
            'mobile': unformatted['Mobile'],
            'email': unformatted['Email'].lower(),
            'gender': unformatted['Gender'].upper(),
            'active': unformatted['Active'] == 'YES',
            'expiry_date': unformatted['ExpieryDate'],
            'card_number': unformatted['CardNumber'],
            'registered_date': unformatted['RegisterdDate'],
            'last_visit_date': unformatted['LastVisitDate'],
            'contract_type': unformatted['CurrentOffering'],
            'contract_number': unformatted['ContractNumber'],
            'contract_start_date': unformatted['ContractStartdate']

        }

    def format_response_list(self, unformatted_list):
        formatted = []
        for resp in unformatted_list:
            formatted.append(self.format_customer_response(resp))
        return formatted
