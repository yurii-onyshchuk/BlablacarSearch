# Generated by Django 4.0.5 on 2022-06-24 12:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='from_coordinate',
            field=models.CharField(max_length=32, verbose_name='Координата відправлення'),
        ),
        migrations.AlterField(
            model_name='task',
            name='to_coordinate',
            field=models.CharField(max_length=32, verbose_name='Координата прибуття'),
        ),
    ]
