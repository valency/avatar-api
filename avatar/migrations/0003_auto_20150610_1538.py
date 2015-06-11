# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('avatar', '0002_clost_occupency'),
    ]

    operations = [
        migrations.RenameField(
            model_name='clost',
            old_name='occupency',
            new_name='occupancy',
        ),
    ]
