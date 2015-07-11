# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('avatar', '0011_clost_ls_trajid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sample',
            name='p',
            field=models.ForeignKey(related_name='sample', to='avatar.Point'),
        ),
        migrations.AlterField(
            model_name='trace',
            name='p',
            field=models.ManyToManyField(related_name='trace', to='avatar.Sample'),
        ),
        migrations.AlterField(
            model_name='trajectory',
            name='trace',
            field=models.ForeignKey(related_name='trajectory', to='avatar.Trace', null=True),
        ),
    ]
