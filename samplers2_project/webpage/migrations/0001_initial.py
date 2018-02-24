# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2018-02-22 00:33
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='OptionToShow',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text_to_show', models.TextField(blank=True, max_length=500)),
                ('order_in_steps', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('facebook_username', models.CharField(blank=True, max_length=255)),
                ('gmail_username', models.CharField(blank=True, max_length=255)),
                ('gender', models.CharField(blank=True, max_length=40)),
                ('bio', models.TextField(blank=True, max_length=500)),
                ('location', models.CharField(blank=True, max_length=30)),
                ('institucion', models.CharField(blank=True, max_length=30)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=30)),
                ('deleted', models.BooleanField(default=False)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webpage.Profile')),
            ],
        ),
        migrations.CreateModel(
            name='Step',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('step_type', models.CharField(blank=True, max_length=30)),
                ('order_in_workflow', models.IntegerField(null=True)),
                ('text_to_show', models.TextField(blank=True, max_length=500)),
                ('sample_test', models.TextField(blank=True, max_length=500)),
                ('max_length', models.IntegerField()),
                ('optional', models.BooleanField(default=False)),
                ('instruct_to_show', models.TextField(blank=True, max_length=500)),
                ('image_to_overlay', models.TextField(blank=True, max_length=500)),
                ('title', models.TextField(blank=True, max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='Workflow',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=30)),
            ],
        ),
        migrations.AddField(
            model_name='step',
            name='workflow',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webpage.Workflow'),
        ),
        migrations.AddField(
            model_name='optiontoshow',
            name='step',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webpage.Step'),
        ),
    ]
