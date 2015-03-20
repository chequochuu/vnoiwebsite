# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0009_auto_20150319_1711'),
    ]

    operations = [
        migrations.AddField(
            model_name='pinnedtopic',
            name='last_updated',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='pinnedtopic',
            name='total_vote',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
