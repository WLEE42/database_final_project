# -*- coding: utf-8 -*-
# Generated by Django 1.11.25 on 2019-11-18 19:26
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('library', '0002_user_is_staff'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='borrow',
            name='expectdate',
        ),
        migrations.AddField(
            model_name='borrow',
            name='isfinished',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='borrow',
            name='bcid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='borrow',
                                    to='library.Bookcopy'),
        ),
    ]
