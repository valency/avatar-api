# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('avatar', '0007_timeslot'),
    ]

    operations = [
        migrations.AddField(
            model_name='clost',
            name='timeslot',
            field=models.ManyToManyField(to='avatar.TimeSlot', null=True),
        ),
    ]
