# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-04-07 06:32
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_auto_20190406_0248'),
    ]

    operations = [
        migrations.AlterField(
            model_name='applicationstatuslink',
            name='application_status',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api.ApplicationStatus'),
        ),
    ]