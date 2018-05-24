from django.test import TestCase

from events.models.guest import Guest

""" Tests the Guest model's functions. """


class TestGuestModel(TestCase):

    def setUp(self):
        self.guest = Guest.objects.create(
            email='username@domain.com', first_name='first_name', last_name='last_name', phone_number=41305325)

    """ Tests the Guest model's str function. """
    def test_guest_str(self):

        # arrange
        guest_name = 'first_name last_name'

        # act
        result = str(self.guest)

        # assert
        self.assertEquals(result, guest_name)
