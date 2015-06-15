# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('avatar', '0009_auto_20150615_0656'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clost',
            name='context',
            field=models.CharField(max_length=131071, null=True),
        ),
    ]
