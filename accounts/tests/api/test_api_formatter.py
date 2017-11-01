from django.test import TestCase
from ...api.exeline import Exeline
from .fixtures.fixtures import get_json_fixture


def mock_request(filename):
    def get(*args):
        return get_json_fixture(filename)
    return get


class ApiFormatterTest(TestCase):
    def test_customer_info_url(self):
        api = Exeline('todd', 'passpass')
        url = api.get_url('customer_in_gym', customer_no="250", gym_id="2")
        self.assertEqual(url, '/Member/2/250/todd/passpass')

    def test_member_for_gym_since_days_url(self):
        api = Exeline('olaf', 'karukaru')
        url = api.get_url('members_for_gym_since_days', gym_id="3", days=10)
        self.assertEqual(url, '/Members/3/10/olaf/karukaru')

    def test_member_for_gym_url(self):
        api = Exeline('olaf', 'karukaru')
        url = api.get_url('members_for_gym', gym_id="4")
        self.assertEqual(url, '/Members/4/olaf/karukaru')
