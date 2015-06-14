# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('avatar', '0004_auto_20150612_0744'),
    ]

    operations = [
        migrations.AddField(
            model_name='clost',
            name='context',
            field=models.TextField(max_length=65535, null=True),
        ),
        migrations.AlterField(
            model_name='clost',
            name='ls_sample',
            field=models.ManyToManyField(to='avatar.Sample', null=True),
        ),
        migrations.AlterField(
            model_name='clost',
            name='ls_traj',
            field=models.ManyToManyField(to='avatar.Trajectory', null=True),
        ),
    ]
