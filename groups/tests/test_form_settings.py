from django.test import TestCase
from ..forms import SettingsForm
from ..models import SportsGroup


class SettingsFormTest(TestCase):
    fixtures = ['groups.json']

    def test_form_has_right_fields(self):
        form = SettingsForm(slug='volleyball')
        expected = ['public']
        self.assertSequenceEqual(expected, list(form.fields))

    def test_group_set_to_private(self):
        form = SettingsForm(
            data={}, slug='volleyball')
        self.assertTrue(form.is_valid())
        group = SportsGroup.objects.get(slug='volleyball')
        self.assertFalse(group.public)

    def test_group_set_to_private_param(self):
        form = SettingsForm(
            data={'public': False}, slug='volleyball')
        self.assertTrue(form.is_valid())
        group = SportsGroup.objects.get(slug='volleyball')
        self.assertFalse(group.public)

    def test_group_set_to_public(self):
        form = SettingsForm(
            data={'public': True}, slug='volleyball')
        self.assertTrue(form.is_valid())
        group = SportsGroup.objects.get(slug='volleyball')
        self.assertTrue(group.public)

    def test_invalid_slug(self):
        form = SettingsForm(
            data={}, slug='bolleyvall')
        self.assertFalse(form.is_valid())
        self.assertEqual(form.non_field_errors(), ['Invalid group'])
