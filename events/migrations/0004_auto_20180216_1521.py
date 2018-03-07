# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-02-16 14:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0003_auto_20180207_2009'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='event',
            options={'verbose_name': 'event', 'verbose_name_plural': 'events'},
        ),
        migrations.AlterModelOptions(
            name='eventdescription',
            options={'verbose_name': 'event description', 'verbose_name_plural': 'event descriptions'},
        ),
        migrations.AlterField(
            model_name='event',
            name='end_date',
            field=models.DateTimeField(verbose_name='end date'),
        ),
        migrations.AlterField(
            model_name='event',
            name='is_host_ntnui',
            field=models.BooleanField(default=False, verbose_name='hosted by NTNUI'),
        ),
        migrations.AlterField(
            model_name='event',
            name='priority',
            field=models.BooleanField(default=False, verbose_name='priority'),
        ),
        migrations.AlterField(
            model_name='event',
            name='sports_group',
            field=models.ManyToManyField(blank=True, null=True, to='groups.SportsGroup', verbose_name='hosted by'),
        ),
        migrations.AlterField(
            model_name='event',
            name='start_date',
            field=models.DateTimeField(verbose_name='start date'),
        ),
        migrations.AlterField(
            model_name='eventdescription',
            name='description_text',
            field=models.CharField(max_length=500, verbose_name='description'),
        ),
        migrations.AlterField(
            model_name='eventdescription',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.Event', verbose_name='event'),
        ),
        migrations.AlterField(
            model_name='eventdescription',
            name='language',
            field=models.CharField(max_length=30, verbose_name='language'),
        ),
        migrations.AlterField(
            model_name='eventdescription',
            name='name',
            field=models.CharField(max_length=100, verbose_name='name'),
        ),
    ]