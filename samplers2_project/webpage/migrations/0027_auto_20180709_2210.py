# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2018-07-09 22:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webpage', '0026_auto_20180709_2203'),
    ]

    operations = [
        migrations.AlterField(
            model_name='routeinformationresult',
            name='accuracy',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='routeinformationresult',
            name='altitude',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='routeinformationresult',
            name='bearing',
            field=models.IntegerField(),
        ),
    ]