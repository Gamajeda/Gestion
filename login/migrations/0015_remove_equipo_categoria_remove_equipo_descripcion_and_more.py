# Generated by Django 5.1.1 on 2024-11-17 00:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0014_ticket_comentarios'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='equipo',
            name='categoria',
        ),
        migrations.RemoveField(
            model_name='equipo',
            name='descripcion',
        ),
        migrations.RemoveField(
            model_name='equipo',
            name='fecha_adquisicion',
        ),
        migrations.RemoveField(
            model_name='equipo',
            name='fecha_ultimo_mantenimiento',
        ),
        migrations.RemoveField(
            model_name='equipo',
            name='marca',
        ),
        migrations.RemoveField(
            model_name='equipo',
            name='modelo',
        ),
        migrations.RemoveField(
            model_name='equipo',
            name='proximo_mantenimiento',
        ),
    ]
