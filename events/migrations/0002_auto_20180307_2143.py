# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-03-07 20:43
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='subeventdescription',
            old_name='sub_event',
            new_name='category',
        ),
    ]
