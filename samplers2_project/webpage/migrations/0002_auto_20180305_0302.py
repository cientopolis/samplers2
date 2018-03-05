# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2018-03-05 03:02
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('webpage', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='optiontoshow',
            name='order_in_steps',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='workflow',
            name='project',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='workflow', to='webpage.Project'),
        ),
    ]
