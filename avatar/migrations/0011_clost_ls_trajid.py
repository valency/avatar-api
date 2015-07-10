# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('avatar', '0010_auto_20150615_0757'),
    ]

    operations = [
        migrations.AddField(
            model_name='clost',
            name='ls_trajid',
            field=models.CharField(max_length=131071, null=True),
        ),
    ]
