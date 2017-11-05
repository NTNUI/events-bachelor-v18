# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-05 12:00
from __future__ import unicode_literals

from django.db import migrations, models
import groups.models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0006_auto_20171105_1233'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sportsgroup',
            name='cover_photo',
            field=models.ImageField(default='cover_photo/ntnui-volleyball.png', upload_to=groups.models.get_cover_upload_to),
        ),
    ]
