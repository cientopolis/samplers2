# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2018-06-28 03:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webpage', '0014_auto_20180626_0000'),
    ]

    operations = [
        migrations.AlterField(
            model_name='locationstepresult',
            name='latitude',
            field=models.DecimalField(decimal_places=8, default=1, max_digits=9),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='locationstepresult',
            name='longitude',
            field=models.DecimalField(decimal_places=8, default=1, max_digits=9),
            preserve_default=False,
        ),
    ]