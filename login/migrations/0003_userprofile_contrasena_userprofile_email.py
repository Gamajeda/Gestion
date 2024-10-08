# Generated by Django 5.1.1 on 2024-10-07 00:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0002_alter_comentario_id_usuario_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='contrasena',
            field=models.CharField(default='default_password', max_length=128),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='email',
            field=models.EmailField(default='default@example.com', max_length=254),
        ),
    ]
