# Generated by Django 4.1.7 on 2023-03-29 20:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_task_link_delete_taskinfo'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='task',
            options={'verbose_name': 'Завдання на пошук поїздок', 'verbose_name_plural': 'Завдання на пошук поїздок'},
        ),
    ]
