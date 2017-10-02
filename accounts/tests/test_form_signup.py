from django.test import TestCase
from ..forms import SignUpForm

class SignUpFormTest(TestCase):
    def test_form_has_right_fields(self):
        form = SignUpForm()
        expected = ['email', 'password1', 'password2']
        self.assertSequenceEqual(expected, list(form.fields))
