# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-19 02:18
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('web_site', '0005_auto_20160519_0006'),
    ]

    operations = [
        migrations.RenameField(
            model_name='searchquery',
            old_name='ideal_dcg',
            new_name='ideal_ndcg',
        ),
        migrations.RenameField(
            model_name='searchquery',
            old_name='lsa_dcg',
            new_name='lsa_ndcg',
        ),
    ]
