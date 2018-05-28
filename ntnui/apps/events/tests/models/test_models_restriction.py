from django.test import TestCase

from events.models.restriction import Restriction

""" Tests the Restriction model's functions. """


class TestRestrictionModel(TestCase):

    def setUp(self):
        self.restriction = Restriction.objects.create(name='name')

    """ Tests the Restriction model's str function. """
    def test_str(self):

        # arrange
        restriction_name = 'name'

        # act
        result = str(self.restriction)

        # assert
        self.assertEquals(result, restriction_name)
