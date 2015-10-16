# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('avatar_core', '__first__'),
        ('avatar_user', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Action',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('point', models.ForeignKey(to='avatar_core.Sample')),
                ('road', models.ForeignKey(to='avatar_core.Road')),
            ],
        ),
        migrations.CreateModel(
            name='HmmEmissionTable',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('table', models.TextField(max_length=65535, null=True)),
                ('city', models.ForeignKey(to='avatar_core.RoadNetwork')),
                ('traj', models.ForeignKey(to='avatar_core.Trajectory')),
            ],
        ),
        migrations.CreateModel(
            name='HmmTransitionTable',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('table', models.TextField(max_length=65535, null=True)),
                ('city', models.ForeignKey(to='avatar_core.RoadNetwork')),
                ('traj', models.ForeignKey(to='avatar_core.Trajectory')),
            ],
        ),
        migrations.CreateModel(
            name='ShortestPathIndex',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('length', models.IntegerField(null=True)),
                ('city', models.ForeignKey(to='avatar_core.RoadNetwork')),
                ('end', models.ForeignKey(related_name='end', to='avatar_core.Intersection')),
                ('path', models.ForeignKey(to='avatar_core.Path')),
                ('start', models.ForeignKey(related_name='start', to='avatar_core.Intersection')),
            ],
        ),
        migrations.CreateModel(
            name='UserActionHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('action', models.ManyToManyField(to='avatar_map_matching.Action')),
                ('traj', models.ForeignKey(to='avatar_core.Trajectory')),
                ('user', models.ForeignKey(to='avatar_user.Account')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='useractionhistory',
            unique_together=set([('user', 'traj')]),
        ),
        migrations.AlterUniqueTogether(
            name='shortestpathindex',
            unique_together=set([('city', 'start', 'end')]),
        ),
        migrations.AlterUniqueTogether(
            name='hmmtransitiontable',
            unique_together=set([('city', 'traj')]),
        ),
        migrations.AlterUniqueTogether(
            name='hmmemissiontable',
            unique_together=set([('city', 'traj')]),
        ),
    ]
