# Generated by Django 4.0.5 on 2022-06-13 15:15

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_city', models.CharField(max_length=32, verbose_name='Звідки?')),
                ('to_city', models.CharField(max_length=32, verbose_name='Куди?')),
                ('from_coordinate', models.CharField(max_length=22, verbose_name='Координата відправлення')),
                ('to_coordinate', models.CharField(max_length=22, verbose_name='Координата прибуття')),
                ('locale', models.CharField(default='uk-UA', max_length=5, verbose_name='Локалізація')),
                ('currency', models.CharField(default='UAH', max_length=3, verbose_name='Валюта')),
                ('start_date_local', models.DateTimeField(default=datetime.datetime.now, verbose_name='Починаючи з часу')),
                ('end_date_local', models.DateTimeField(blank=True, null=True, verbose_name='Закінчуючи часом')),
                ('requested_seats', models.IntegerField(default=1, verbose_name='Кількість місць')),
                ('radius_in_meters', models.IntegerField(blank=True, null=True, verbose_name='Радіус пошуку, м')),
                ('notification', models.BooleanField(default=False, verbose_name='Отримувати сповіщення про нові поїздки')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Користувач')),
            ],
            options={
                'verbose_name': 'Пошук поїздок',
                'verbose_name_plural': 'Пошук поїздок',
            },
        ),
        migrations.CreateModel(
            name='TaskInfo',
            fields=[
                ('link', models.URLField(blank=True, null=True, verbose_name='Посилання на пошук поїздку')),
                ('count', models.IntegerField(blank=True, null=True, verbose_name='Загальна кількість знайдених поїздок')),
                ('full_trip_count', models.IntegerField(blank=True, null=True, verbose_name='Загальна кількість знайдених повних поїздок')),
                ('task', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='main.task')),
            ],
            options={
                'verbose_name': 'Інформація щодо пошуку поїздки',
                'verbose_name_plural': 'Інформація щодо пошуку поїздок',
            },
        ),
        migrations.CreateModel(
            name='Trip',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('link', models.URLField(verbose_name='Посилання на поїздку')),
                ('from_city', models.CharField(max_length=32, verbose_name='Пункт відправлення')),
                ('from_address', models.CharField(blank=True, max_length=128, null=True, verbose_name='Адреса відправлення')),
                ('departure_time', models.DateTimeField(verbose_name='Час відправлення')),
                ('to_city', models.CharField(max_length=32, verbose_name='Пункт прибуття')),
                ('to_address', models.CharField(blank=True, max_length=128, null=True, verbose_name='Адреса прибуття')),
                ('arrival_time', models.DateTimeField(verbose_name='Час прибуття')),
                ('price', models.CharField(max_length=16, verbose_name='Ціна')),
                ('vehicle', models.CharField(blank=True, max_length=32, null=True, verbose_name='Автомобіль')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.task', verbose_name='Завдання')),
            ],
            options={
                'verbose_name': 'Знайдена поїздок',
                'verbose_name_plural': 'Знайдені поїздки',
                'ordering': ('departure_time',),
            },
        ),
    ]
