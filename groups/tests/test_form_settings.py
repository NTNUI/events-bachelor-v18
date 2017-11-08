from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from ..forms import SettingsForm
from ..models import SportsGroup
from groups import views as group_views
from django.core.urlresolvers import reverse


class SettingsFormTest(TestCase):
    fixtures = ['complete.json']

    def test_form_has_right_fields(self):
        form = SettingsForm(slug='volleyball')
        expected = ['public', 'description', 'thumbnail', 'cover_photo']
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

    def test_upload_thumbnail(self):
        image = SimpleUploadedFile(name="test_image.jpg", content=open("ntnui/static/img/ntnui-icon.png", 'rb').read(),
                                   content_type="image/jpeg")
        form = SettingsForm(data={'thumbnail': image}, slug='volleyball')
        self.assertTrue(form.is_valid())

    def test_upload_cover_photo(self):
        image = SimpleUploadedFile(name="test_image.jpg", content=open("ntnui/static/img/ntnui-icon.png", 'rb').read(),
                                   content_type="image/jpeg")
        form = SettingsForm(data={'cover_photo': image}, slug='volleyball')
        self.assertTrue(form.is_valid())

    def test_description(self):
        form = SettingsForm(data={'description': "See you space cowboy.."}, slug='volleyball')
        self.assertTrue(form.is_valid())
        form.set_description()
        group = SportsGroup.objects.get(slug='volleyball')
        self.assertEqual(group.description, "See you space cowboy..")
