# Generated by Django 3.1.3 on 2020-12-16 19:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trainer', '0007_auto_20201207_1551'),
    ]

    operations = [
        migrations.RenameField(
            model_name='setting',
            old_name='ignore_in_brackets',
            new_name='import_ignore_in_brackets',
        ),
        migrations.AddField(
            model_name='setting',
            name='exact_match',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='setting',
            name='record_stats',
            field=models.BooleanField(default=False),
        ),
    ]