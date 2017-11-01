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
