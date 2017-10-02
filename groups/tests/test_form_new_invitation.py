from django.test import TestCase
from ..forms import NewInvitationForm

class InvitationFormTest(TestCase):
    def test_form_has_right_fields(self):
        form = NewInvitationForm(slug='volleyball')
        expected = ['email']
        self.assertSequenceEqual(expected, list(form.fields))


    # test the validation process
    #def test_should_throw_if_no_group_slug(self):
    #    form = NewInvitationForm()
    #    self.assertFalse(form.is_valid())
    #    self.assertFormError(form, 'form', None, 'Some error')
