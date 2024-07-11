# Generated by Django 4.1.7 on 2024-07-11 09:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0014_trip_trip_hash'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='from_city',
            field=models.CharField(max_length=64, verbose_name='Звідки?'),
        ),
        migrations.AlterField(
            model_name='task',
            name='from_coordinate',
            field=models.CharField(max_length=64, verbose_name='Координата відправлення'),
        ),
        migrations.AlterField(
            model_name='task',
            name='to_city',
            field=models.CharField(max_length=64, verbose_name='Куди?'),
        ),
        migrations.AlterField(
            model_name='task',
            name='to_coordinate',
            field=models.CharField(max_length=64, verbose_name='Координата прибуття'),
        ),
    ]