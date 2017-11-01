
class ApiFormatter(object):

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
            'first_name': unformatted['FirstName'],
            'last_name': unformatted['LastName'],
            'birth_date': unformatted['BirthDate'],
            'mobile': unformatted['Mobile'],
            'email': unformatted['Email'],
            'gender': unformatted['Gender'],
            'active': unformatted['Active'] == 'YES',
            'expiry_date': unformatted['ExpieryDate'],
            'card_number': unformatted['CardNumber'],
            'registered_date': unformatted['RegisterdDate'],
            'last_visit_date': unformatted['LastVisitDate'],
            'contract_type': unformatted['CurrentOffering'],
            'contract_number': unformatted['ContractNumber'],
            'contract_start_date': unformatted['ContractStartdate']

        }
