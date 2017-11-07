from django.test import TestCase
from ...api.formatter import ApiFormatter
from .fixtures.fixtures import get_json_fixture


class ApiFormatterTest(TestCase):
    def test_should_format_customer(self):
        unfiltered_response = get_json_fixture('customer-response.json')
        formatter = ApiFormatter()
        formatted = formatter.format_customer_response(unfiltered_response)
        expected = get_json_fixture('customer-response-formatted.json')
        self.assertEqual(formatted, expected)

    def test_should_format_every_customer_in_list(self):
        unfiltered_response = get_json_fixture('gym-response.json')
        formatter = ApiFormatter()
        formatted = formatter.format_response_list(unfiltered_response)
        expected = get_json_fixture('gym-response-formatted.json')
        self.assertEqual(formatted, expected)

    def test_should_format_all_caps_name(self):
        name = 'RANVEIG OLSEN'
        formatted = ApiFormatter().capital_first_letter(name)
        self.assertEqual(formatted, 'Ranveig Olsen')

    def test_should_format_all_lower_name(self):
        name = 'kari knutsen'
        formatted = ApiFormatter().capital_first_letter(name)
        self.assertEqual(formatted, 'Kari Knutsen')

    def test_should_format_middle_names(self):
        name = 'Jon m Tyrifjord'
        formatted = ApiFormatter().capital_first_letter(name)
        self.assertEqual(formatted, 'Jon M Tyrifjord')
