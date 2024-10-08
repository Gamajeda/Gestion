from django.db import models

# Create your models here.

class Categoria(models.Model):
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre

class UserProfile(models.Model):
    usuario = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    email = models.EmailField(default='example@example.com')
    nombre = models.CharField(max_length=50, default='Sin Nombre')
    apellidos = models.CharField(max_length=30, default='Sin Apellido')
    password = models.CharField(max_length=50, default='1234')

    telefono = models.CharField(max_length=15, default='123456789')


    def __str__(self):
        return self.usuario.username


class Ticket(models.Model):
    PRIORIDAD_CHOICES = [
        ('B', 'Baja'),
        ('M', 'Media'),
        ('A', 'Alta')
    ]
    ESTADO_CHOICES = [
        ('P', 'Pendiente'),
        ('R', 'Resuelto')
    ]
    titulo = models.CharField(max_length=50)
    descripcion = models.TextField()
    prioridad = models.CharField(max_length=1, choices=PRIORIDAD_CHOICES)
    categoria = models.ForeignKey('Categoria', on_delete=models.CASCADE)
    estado = models.CharField(max_length=1, choices=ESTADO_CHOICES, default='P')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)
    usuario = models.ForeignKey('UserProfile', on_delete=models.CASCADE)

    def __str__(self):
        return self.titulo
