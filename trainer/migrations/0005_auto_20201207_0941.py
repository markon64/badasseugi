# Generated by Django 3.1.3 on 2020-12-07 14:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trainer', '0004_auto_20201207_0859'),
    ]

    operations = [
        migrations.AlterField(
            model_name='problem',
            name='audio_file',
            field=models.CharField(blank=True, default=None, max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='problem',
            name='translation',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]
