# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-03-29 06:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20190306_2108'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='applicationstatus',
            options={'get_latest_by': ['order', 'date', 'created_at'], 'verbose_name_plural': 'application_statuses'},
        ),
        migrations.AlterField(
            model_name='companyrating',
            name='sample_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]