# Generated by Django 3.2.4 on 2021-10-30 20:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trainer', '0022_trainingqueue_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='setting',
            name='dark_mode',
            field=models.BooleanField(default=False),
        ),
    ]
