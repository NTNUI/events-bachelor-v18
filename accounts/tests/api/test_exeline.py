from django.test import TestCase
from ...api.exeline import Exeline


VALID_CUSTOMER_NO = 30
INVALID_CUSTOMER_NO = 20


class ExelineTest(TestCase):
    def test_stores_username_and_password(self):
        api = Exeline('user', 'pass')
        self.assertEqual('user', api.username)
        self.assertEqual('pass', api.password)

    def test_shoud_get_customer_info_for_valid_customer(self):
        api = Exeline('user', 'pass')
        response = api.get_customer_info(1, VALID_CUSTOMER_NO)
        self.assertEqual(
            {'customerNo': VALID_CUSTOMER_NO, 'name': 'Roar'}, response)

    def test_shoud_get_customer_info_for_invalid_customer(self):
        api = Exeline('user', 'pass')
        response = api.get_customer_info(1, INVALID_CUSTOMER_NO)
        expected_response = {
            "GetMemberByIdResult": {
                "Members": None,
                "Status": {
                    "StatusCode": "2",
                    "StatusMessage": "No Members Found",
                    "CustomerId": 0,
                    "GuardianCustomerId": 0,
                    "ExpirationDate": None
                }
            }
        }
        self.assertEqual(expected_response, response)
