# Generated by Django 4.1.7 on 2023-03-27 16:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_delete_apikey'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='link',
            field=models.URLField(blank=True, null=True, verbose_name='Посилання на пошук поїздок за завданням'),
        ),
        migrations.DeleteModel(
            name='TaskInfo',
        ),
    ]
