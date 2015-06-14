# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('avatar', '0003_auto_20150610_1538'),
    ]

    operations = [
        migrations.AddField(
            model_name='clost',
            name='ls_sample',
            field=models.ManyToManyField(to='avatar.Sample'),
        ),
        migrations.AddField(
            model_name='clost',
            name='ls_traj',
            field=models.ManyToManyField(to='avatar.Trajectory'),
        ),
    ]
