# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2018-05-31 01:40
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('webpage', '0007_project_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='created_date',
            field=models.DateTimeField(default=datetime.datetime(2018, 5, 31, 1, 40, 0, 101225, tzinfo=utc), editable=False),
            preserve_default=False,
        ),
    ]