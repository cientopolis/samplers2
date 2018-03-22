# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2018-03-21 22:30
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
                ('order_in_steps', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='ParticipantsGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_owner', models.BooleanField(default=False)),
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
                ('participants', models.ManyToManyField(through='webpage.ParticipantsGroup', to='webpage.Profile')),
            ],
        ),
        migrations.CreateModel(
            name='Step',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('step_type', models.CharField(choices=[('DateStep', 'DateStep'), ('TextStep', 'TextStep'), ('InformationStep', 'InformationStep'), ('PhotoStep', 'PhotoStep'), ('LocationStep', 'LocationStep'), ('SelectOneStep', 'SelectOneStep'), ('SelectMultipleStep', 'SelectMultipleStep'), ('TimeStep', 'TimeStep')], max_length=30)),
                ('order_in_workflow', models.IntegerField()),
                ('text_to_show', models.TextField(blank=True, max_length=500)),
                ('sample_test', models.TextField(blank=True, max_length=500)),
                ('max_length', models.IntegerField(blank=True, null=True)),
                ('optional', models.NullBooleanField()),
                ('input_type', models.CharField(blank=True, choices=[('number', 'number'), ('text', 'text'), ('decimal', 'decimal')], max_length=1)),
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
                ('project', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='workflow', to='webpage.Project')),
            ],
        ),
        migrations.AddField(
            model_name='step',
            name='workflow',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='steps', to='webpage.Workflow'),
        ),
        migrations.AddField(
            model_name='participantsgroup',
            name='profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webpage.Profile'),
        ),
        migrations.AddField(
            model_name='participantsgroup',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webpage.Project'),
        ),
        migrations.AddField(
            model_name='optiontoshow',
            name='step',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='options_to_show', to='webpage.Step'),
        ),
    ]
