# Generated by Django 3.2.4 on 2021-09-01 20:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trainer', '0018_auto_20210901_1106'),
    ]

    operations = [
        migrations.AddField(
            model_name='trainingqueueitem',
            name='item_number',
            field=models.IntegerField(default=0),
        ),
    ]
