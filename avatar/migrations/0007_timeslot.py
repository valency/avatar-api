# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('avatar', '0006_auto_20150614_0527'),
    ]

    operations = [
        migrations.CreateModel(
            name='TimeSlot',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('starttime', models.DateTimeField()),
                ('timeslot', models.IntegerField(null=True)),
                ('bounding_box', models.ForeignKey(to='avatar.Rect')),
                ('ls_sample', models.ManyToManyField(to='avatar.Sample', null=True)),
                ('ls_traj', models.ManyToManyField(to='avatar.Trajectory', null=True)),
            ],
        ),
    ]
