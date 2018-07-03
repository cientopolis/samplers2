# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2018-07-01 16:05
from __future__ import unicode_literals

from django.db import migrations, models
import webpage.models


class Migration(migrations.Migration):

    dependencies = [
        ('webpage', '0019_auto_20180630_0321'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='resourcestepresult',
            name='resource_path',
        ),
        migrations.AddField(
            model_name='resourcestepresult',
            name='file',
            field=models.FileField(default=1, upload_to=webpage.models.workflow_result_directory_path),
            preserve_default=False,
        ),
    ]
