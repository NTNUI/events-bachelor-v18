# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-31 10:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forms', '0002_auto_20171030_1203'),
    ]

    operations = [
        migrations.AddField(
            model_name='boardchange',
            name='name',
            field=models.CharField(default='Board Change Form', max_length=100),
        ),
    ]
