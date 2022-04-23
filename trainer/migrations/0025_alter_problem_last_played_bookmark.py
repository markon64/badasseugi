# Generated by Django 4.0.4 on 2022-04-19 07:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('trainer', '0024_setting_hide_translation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='problem',
            name='last_played',
            field=models.DateTimeField(blank=True, null=True, verbose_name='last played'),
        ),
        migrations.CreateModel(
            name='Bookmark',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fake_problem_number', models.IntegerField()),
                ('name', models.CharField(max_length=100)),
                ('problem_set', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trainer.problemset')),
            ],
        ),
    ]
