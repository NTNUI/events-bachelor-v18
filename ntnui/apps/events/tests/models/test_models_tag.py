from django.test import TestCase

from events.models.tag import Tag

""" Tests the Tag model's functions. """


class TestTagModel(TestCase):

    def setUp(self):
        self.tag = Tag.objects.create(name='name')

    """ Tests the Tag model's str function. """
    def test_str(self):

        # arrange
        tag_name = 'name'

        # act
        result = str(self.tag)

        # assert
        self.assertEquals(result, tag_name)
