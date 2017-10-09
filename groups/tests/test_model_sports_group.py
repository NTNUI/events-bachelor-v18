from django.test import TestCase
from groups.models import SportsGroup


class SportsGroupTestCase(TestCase):
    def setUp(self):
        SportsGroup.objects.create(name="NTNUI Roing", description="Vi ror")

    def test_have_name(self):
        group = SportsGroup.objects.get(name="NTNUI Roing")
        self.assertEqual(group.name, 'NTNUI Roing')

    def test_have_description(self):
        group = SportsGroup.objects.get(name="NTNUI Roing")
        self.assertEqual(group.description, "Vi ror")
