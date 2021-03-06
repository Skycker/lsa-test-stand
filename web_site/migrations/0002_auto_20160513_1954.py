# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-13 19:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web_site', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=128)),
            ],
        ),
        migrations.AddField(
            model_name='document',
            name='group',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='web_site.DocumentGroup'),
            preserve_default=False,
        ),
    ]
