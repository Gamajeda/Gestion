# Generated by Django 5.1.1 on 2024-10-14 06:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0003_equipo'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='equipo',
            field=models.ForeignKey(blank=True, default=1, on_delete=django.db.models.deletion.CASCADE, to='login.equipo'),
        ),
        migrations.AlterField(
            model_name='equipo',
            name='nombre',
            field=models.CharField(default='Equipo Desconocido', max_length=100),
        ),
    ]
