# Generated by Django 5.1.1 on 2024-11-17 00:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0013_problemafrecuente_calificacion'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='comentarios',
            field=models.TextField(blank=True, null=True),
        ),
    ]
