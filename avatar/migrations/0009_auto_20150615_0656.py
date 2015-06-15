# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('avatar', '0008_clost_timeslot'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='clost',
            name='timeslot',
        ),
        migrations.AddField(
            model_name='clost',
            name='starttime',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='clost',
            name='timenode',
            field=models.ManyToManyField(to='avatar.TimeSlot'),
        ),
        migrations.AlterField(
            model_name='clost',
            name='ls_sample',
            field=models.ManyToManyField(to='avatar.Sample'),
        ),
        migrations.AlterField(
            model_name='clost',
            name='ls_traj',
            field=models.ManyToManyField(to='avatar.Trajectory'),
        ),
        migrations.AlterField(
            model_name='timeslot',
            name='ls_sample',
            field=models.ManyToManyField(to='avatar.Sample'),
        ),
        migrations.AlterField(
            model_name='timeslot',
            name='ls_traj',
            field=models.ManyToManyField(to='avatar.Trajectory'),
        ),
    ]
