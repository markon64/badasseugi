# Generated by Django 3.1.3 on 2020-12-04 13:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trainer', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='problemset',
            name='audio_file',
        ),
        migrations.AddField(
            model_name='problem',
            name='success_number',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='problemset',
            name='last_fake_problem_number',
            field=models.IntegerField(default=0),
        ),
    ]
