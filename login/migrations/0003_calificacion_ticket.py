# Generated by Django 5.1.1 on 2024-11-30 21:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0002_equipo_problemafrecuente_ticket_archivo_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='calificacion',
            name='ticket',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='calificaciones_ticket', to='login.ticket'),
            preserve_default=False,
        ),
    ]