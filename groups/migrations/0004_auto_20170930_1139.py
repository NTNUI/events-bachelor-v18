# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-30 11:39
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0003_membership_paid_internal_license'),
    ]

    operations = [
        migrations.RenameField(
            model_name='membership',
            old_name='paid_internal_license',
            new_name='paid',
        ),
    ]