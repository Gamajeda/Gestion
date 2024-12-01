from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model


# Define el modelo de usuario
User = get_user_model()

class ProblemaFrecuente(models.Model):
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField()
    solucion = models.TextField()
    promedio_calificacion = models.FloatField(default=0.0)  # Campo para almacenar el promedio de calificaciones

    def __str__(self):
        return self.titulo





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
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    email = models.EmailField(default='default@example.com', null=False)
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)
    foto = models.ImageField(upload_to='fotos_perfil/', null=True, blank=True)
    nombre = models.CharField(max_length=50)
    apellidos = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.user.username} - {self.rol.nombre}"



class Invitacion(models.Model):
    email = models.EmailField()
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)
    token = models.CharField(max_length=32, unique=True)
    usado = models.BooleanField(default=False)

    def __str__(self):
        return self.email

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
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)
    usuario = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='tickets_usuario')
    encargado = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='tickets_encargado', null=True, blank=True)
    comentarios = models.TextField(blank=True, null=True)
    calificacion = models.IntegerField(null=True, blank=True)  # Permite valores nulos
    historial = models.ManyToManyField(UserProfile, through='HistorialTecnico')
    archivo = models.FileField(upload_to='archivos/', null=True, blank=True)
    

    def save(self, *args, **kwargs):
        if self.pk:  # Si el ticket ya existe, significa que está siendo editado
            old_ticket = Ticket.objects.get(pk=self.pk)
            # Compara si se cambió el encargado o el estado
            if old_ticket.encargado != self.encargado:
                # Crea un registro en el historial
                HistorialTecnico.objects.create(ticket=self, tecnico=self.encargado, fecha_cambio=timezone.now())
            if old_ticket.estado != self.estado:
                # Crea un registro en el historial
                HistorialTecnico.objects.create(ticket=self, tecnico=self.encargado, fecha_cambio=timezone.now(), motivo='Cambio de estado')
            if old_ticket.fecha_resolucion and not self.fecha_resolucion:
                # Si se elimina la fecha de resolución, se elimina el historial
                self.fecha_resolucion = old_ticket.fecha_resolucion
        super(Ticket, self).save(*args, **kwargs)

    def get_mes_creacion(self):
        return self.fecha_creacion.month

    def esta_por_vencer(self):
        if self.fecha_resolucion:
            # Asegurarse de que ambas fechas sean aware
            fecha_resolucion = timezone.make_aware(self.fecha_resolucion) if timezone.is_naive(self.fecha_resolucion) else self.fecha_resolucion
            return (fecha_resolucion - timezone.now()).days <= 3
        return False

    def __str__(self):
        return f"{self.titulo} - {self.id_ticket}"


class HistorialTecnico(models.Model):
    ticket = models.ForeignKey('Ticket', on_delete=models.CASCADE)
    tecnico = models.ForeignKey('UserProfile', on_delete=models.SET_NULL, null=True)
    fecha_cambio = models.DateTimeField(default=timezone.now)
    motivo = models.CharField(max_length=255, null=True, blank=True)  # Nuevo campo motivo

    def __str__(self):
        return f"Historial para {self.ticket} - Técnico: {self.tecnico}"

    def nombre_tecnico(self):
        return self.tecnico.nombre

    def cambio(self):
        return self.fecha_cambio.strftime('%d/%m/%Y %H:%M')

class Calificaciontrabajo(models.Model):
    problema = models.ForeignKey('ProblemaFrecuente', on_delete=models.CASCADE, related_name='calificaciones_trabajo')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    calificacion = models.IntegerField()
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='calificaciones_ticket')  # Añadir related_name
    

    def __str__(self):
        return f"{self.usuario.username} - {self.problema.titulo} - {self.calificacion}"

class Calificacionproblema(models.Model):
    problema = models.ForeignKey('ProblemaFrecuente', on_delete=models.CASCADE, related_name='calificaciones')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    calificacion = models.IntegerField()

    def __str__(self):
        return f"{self.usuario.username} - {self.problema.titulo} - {self.calificacion}"