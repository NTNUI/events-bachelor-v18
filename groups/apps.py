from django.apps import AppConfig
from groups.models import SportsGroup  # , GroupImage
from django.db.models.signals import post_save


class GroupsConfig(AppConfig):
    name = 'groups'

    # def add_default_group_image(self, sender, **kwargs):
    #     group = kwargs['instance']
    #     if kwargs['created']:
    #         image = GroupImage.objects.get(name='default')
    #         group.groupImage.add(image)
    #
    # def ready(self):
    #     post_save.connect(self.add_default_group_image, sender=SportsGroup)
