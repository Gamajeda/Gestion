from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

# Define el modelo de usuario


class ProblemaFrecuente(models.Model):
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField()
    solucion = models.TextField()
    promedio_calificacion = models.FloatField(default=0.0)  # Campo para almacenar el promedio de calificaciones

    def __str__(self):
        return self.titulo

class Calificacion(models.Model):
    problema = models.ForeignKey(ProblemaFrecuente, on_delete=models.CASCADE, related_name='calificaciones')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    calificacion = models.IntegerField()

    def __str__(self):
        return f"{self.usuario.username} - {self.problema.titulo} - {self.calificacion}"

User = get_user_model()

class Rol(models.Model):
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre



class CustomUser(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # Almacena el hash de la contraseña
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.username

class UserProfile(models.Model):
    ROL_CHOICES = [
        ('Tecnico', 'Técnico'),
        ('Cliente', 'Cliente'),
        ('Administrador', 'Administrador'),
    ]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    email = models.EmailField(default='default@example.com', null=False)
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)
    foto = models.ImageField(upload_to='fotos_perfil/', null=True, blank=True)
    nombre = models.CharField(max_length=50)
    apellidos = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.user.username} - {self.rol.nombre}"



class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(default='Sin Descripción')  # Default for descripcion
    termino = models.CharField(max_length=5, default='N/A')  # Default value added for termino

    def __str__(self):
        return self.nombre

class Equipo(models.Model):
    nombre = models.CharField(max_length=100, default='Equipo Desconocido')  # Nombre del aparato
    estado = models.CharField(max_length=50, choices=[('nuevo', 'Nuevo'), ('usado', 'Usado')])  # Estado del aparato
    numero_serie = models.CharField(max_length=50, unique=True)  # Número de serie
    ubicacion = models.CharField(max_length=100, blank=True)  # Ubicación donde se encuentra el aparato

    def __str__(self):
        return f"{self.nombre} - {self.numero_serie}"

class Ticket(models.Model):
    id_ticket = models.AutoField(primary_key=True)
    PRIORIDAD_CHOICES = [
        ('B', 'Baja'),
        ('M', 'Media'),
        ('A', 'Alta'),
    ]
    ESTADO_CHOICES = [
        ('P', 'Pendiente'),
        ('R', 'Resuelto'),
    ]
    
    titulo = models.CharField(max_length=50, null=False)
    descripcion = models.TextField(null=False)
    prioridad = models.CharField(max_length=1, choices=PRIORIDAD_CHOICES, null=False)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, null=False)
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, null=False, blank=True, default=1)
    estado = models.CharField(max_length=1, choices=ESTADO_CHOICES, default='P', null=False)
    fecha_creacion = models.DateTimeField(default=timezone.now, null=False)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)
    usuario = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='tickets_usuario')
    encargado = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='tickets_encargado', null=True, blank=True)
    comentarios = models.TextField(blank=True, null=True)
    calificacion = models.IntegerField(null=True, blank=True)  # Permite valores nulos

    def get_prioridad_display(self):
        return dict(self.PRIORIDAD_CHOICES).get(self.prioridad, 'Desconocida')

    def get_estado_display(self):
        return dict(self.ESTADO_CHOICES).get(self.estado, 'Desconocido')

    def __str__(self):
        return f"{self.titulo} - {self.id_ticket}"
