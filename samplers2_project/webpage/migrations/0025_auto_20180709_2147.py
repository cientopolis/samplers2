# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2018-07-09 21:47
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('webpage', '0024_auto_20180709_2146'),
    ]

    operations = [
        migrations.RenameField(
            model_name='routeinformationresult',
            old_name='accurracy',
            new_name='accuracy',
        ),
    ]