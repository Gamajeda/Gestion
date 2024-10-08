from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
User = get_user_model()

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(default='example@example.com')
    nombre = models.CharField(max_length=50, default='Sin Nombre')
    apellidos = models.CharField(max_length=30, default='Sin Apellido')
    password = models.CharField(max_length=50, default='1234')

    telefono = models.CharField(max_length=15, default='123456789')


    def __str__(self):
        return self.user.username  # Cambiado aquí



class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(default='Sin Descripción')  # Default for descripcion
    termino = models.CharField(max_length=5, default='N/A')  # Default value added for termino

    def __str__(self):
        return self.nombre




class Ticket(models.Model):
    PRIORIDAD_CHOICES = [
        ('B', 'Baja'),
        ('M', 'Media'),
        ('A', 'Alta'),
    ]
    ESTADO_CHOICES = [
        ('P', 'Pendiente'),
        ('R', 'Resuelto'),
    ]
    
    titulo = models.CharField(max_length=50)
    descripcion = models.TextField()
    prioridad = models.CharField(max_length=1, choices=PRIORIDAD_CHOICES)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    estado = models.CharField(max_length=1, choices=ESTADO_CHOICES, default='P')
    fecha_creacion = models.DateTimeField(null=True, blank=True)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)  # Cambiado aquí

    def __str__(self):
        return self.titulo
