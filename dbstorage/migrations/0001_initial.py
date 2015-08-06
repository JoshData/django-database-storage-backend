# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='StoredFile',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('path', models.CharField(help_text='The file name of the stored file.', max_length=256, db_index=True, unique=True)),
                ('mime_type', models.CharField(null=True, help_text='The MIME type of the stored file, if known.', max_length=128, blank=True)),
                ('value', models.TextField(help_text='The encoded binary data in this file.')),
                ('size', models.IntegerField(help_text='The size of the stored file in bytes (the size of the actual file, not as it is stored).', db_index=True)),
                ('encoded_size', models.IntegerField(help_text='The size of the stored file in bytes, as stored.', db_index=True)),
                ('encoding', models.IntegerField(choices=[(0, 'None.'), (1, 'Base 64')])),
                ('gzipped', models.BooleanField()),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated', models.DateTimeField(auto_now=True, db_index=True)),
            ],
        ),
    ]
