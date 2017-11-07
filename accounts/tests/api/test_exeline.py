from django.test import TestCase
from ...api.exeline import Exeline
from .fixtures.fixtures import get_json_fixture

VALID_CUSTOMER_NO = 30
INVALID_CUSTOMER_NO = 20


def mock_request(filename):
    def get(*args):
        return {
            "GetMemberDataResult": {
                "Members": get_json_fixture(filename)
            }
        }
    return get


class ExelineUrlTest(TestCase):
    def test_customer_info_url(self):
        api = Exeline('todd', 'passpass')
        url = api.get_url('customer_in_gym', customer_number="250", gym_id="2")
        self.assertEqual(url, '/Member/2/250/todd/passpass')

    def test_member_for_gym_since_days_url(self):
        api = Exeline('olaf', 'karukaru')
        url = api.get_url('members_for_gym_since_days', gym_id="3", days=10)
        self.assertEqual(url, '/Members/3/10/olaf/karukaru')

    def test_member_for_gym_url(self):
        api = Exeline('olaf', 'karukaru')
        url = api.get_url('members_for_gym', gym_id="4")
        self.assertEqual(url, '/Members/4/olaf/karukaru')


class ExelineTest(TestCase):
    def test_stores_username_and_password(self):
        api = Exeline('user', 'pass')
        self.assertEqual('user', api.username)
        self.assertEqual('pass', api.password)

    def test_shoud_get_customer_info_for_valid_customer(self):
        """Should show customer info for valid customer from API"""
        api = Exeline('user', 'pass')
        api.request = mock_request('customer-response.json')
        response = api.get_customer_info(1, VALID_CUSTOMER_NO)
        self.assertEqual(
            get_json_fixture('customer-response.json'), response)
        pass

    def test_shoud_get_customer_info_for_invalid_customer(self):
        """Should show error for getting invalid customer from API"""
        api = Exeline('user', 'pass')
        api.request = mock_request('found-no-user.json')
        response = api.get_customer_info(1, INVALID_CUSTOMER_NO)
        expected_response = get_json_fixture('found-no-user.json')
        self.assertEqual(expected_response, response)

    def test_should_get_all_members_for_a_gym(self):
        """Get all members for a gym from API"""
        api = Exeline('user', 'pass')
        api.request = mock_request('gym-response.json')
        response = api.get_members_for_gym("2")
        expected_response = get_json_fixture('gym-response.json')
        self.assertEqual(expected_response, response)

    def test_should_get_all_members_for_all_gyms(self):
        """Get all members for all gyms from API"""
        api = Exeline('user', 'pass')
        api.request = mock_request('gym-response.json')
        response = api.get_members_for_all_gyms()
        single_response = get_json_fixture('gym-response.json')
        expected = {
            '1': single_response,
            '2': single_response,
            '3': single_response,
            '4': single_response,
            '5': single_response
        }
        self.assertEqual(expected, response)

    def test_should_get_all_members_for_all_gyms_since_days(self):
        """Get all members for all gyms since days from API"""
        api = Exeline('user', 'pass')
        api.request = mock_request('gym-response.json')
        response = api.get_members_for_all_gyms_since(10)
        single_response = get_json_fixture('gym-response.json')
        expected = {
            '1': single_response,
            '2': single_response,
            '3': single_response,
            '4': single_response,
            '5': single_response
        }
        self.assertEqual(expected, response)

    def test_should_get_all_members_for_a_gym_since_days(self):
        """Get all members for one gym since days from API"""
        api = Exeline('user', 'pass')
        api.request = mock_request('gym-response.json')
        response = api.get_members_for_gym_since("3", 2)
        expected = get_json_fixture('gym-response.json')
        self.assertEqual(expected, response)
