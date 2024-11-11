from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import get_user_model

# Define el modelo de usuario


class ProblemaFrecuente(models.Model):
    descripcion = models.CharField(max_length=255)
    solucion = models.TextField()

    def __str__(self):
        return self.descripcion



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
    descripcion = models.TextField(blank=True)  # Descripción del aparato
    fecha_adquisicion = models.DateField()  # Fecha de adquisición
    estado = models.CharField(max_length=50, choices=[('nuevo', 'Nuevo'), ('usado', 'Usado')])  # Estado del aparato
    marca = models.CharField(max_length=50)  # Marca del aparato
    modelo = models.CharField(max_length=50)  # Modelo del aparato
    numero_serie = models.CharField(max_length=50, unique=True)  # Número de serie
    categoria = models.CharField(max_length=50)  # Categoría del aparato
    ubicacion = models.CharField(max_length=100, blank=True)  # Ubicación donde se encuentra el aparato
    fecha_ultimo_mantenimiento = models.DateField(null=True, blank=True)  # Fecha del último mantenimiento
    proximo_mantenimiento = models.DateField(null=True, blank=True)  # Fecha del próximo mantenimiento

    def __str__(self):
        return f"{self.nombre} - {self.marca} {self.modelo} ({self.numero_serie})"

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
    
    titulo = models.CharField(max_length=50, null=False)  # No se permite nulo
    descripcion = models.TextField(null=False)  # No se permite nulo
    prioridad = models.CharField(max_length=1, choices=PRIORIDAD_CHOICES, null=False)  # No se permite nulo
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, null=False)  # No se permite nulo
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, null=False, blank=True, default=1)
    estado = models.CharField(max_length=1, choices=ESTADO_CHOICES, default='P', null=False)  # Puedes mantener default='P'
    fecha_creacion = models.DateTimeField(default=timezone.now, null=False)  # No se permite nulo
    fecha_resolucion = models.DateTimeField(null=True, blank=True)  # Puede ser nulo y en blanco
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tickets_usuario')  # Sin default
    encargado = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='tickets_encargado', null=True, blank=True)

    def __str__(self):
        return self.titulo

