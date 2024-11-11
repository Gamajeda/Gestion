from django import forms
from .models import Ticket, Categoria, UserProfile, Rol, Equipo, ProblemaFrecuente
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

# Formulario para crear una categoría

class ProblemaFrecuenteForm(forms.ModelForm):
    class Meta:
        model = ProblemaFrecuente
        fields = ['descripcion', 'solucion']

User=get_user_model()


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion', 'termino']
        labels = {
            'nombre': 'Nombre',
            'descripcion': 'Descripción',
            'termino': 'Término'
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
            'termino': forms.TextInput(attrs={'class': 'form-control'})
        }



class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['titulo', 'descripcion' ,'estado' , 'prioridad', 'categoria', 'equipo' , 'usuario', 'encargado']  # Eliminado 'encargado'
        labels = {
            'titulo': 'Título',
            'descripcion': 'Descripción',
            'estado': 'Estado',
            'prioridad': 'Prioridad',
            'categoria': 'Categoría',
            'equipo': 'Equipo',
            'usuario': 'Usuario',
            'encargado': 'Encargado'
        }
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'prioridad': forms.Select(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'equipo': forms.Select(attrs={'class': 'form-control'}),
            'usuario': forms.Select(attrs={'class': 'form-control'}),
            'encargado': forms.Select(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super(TicketForm, self).__init__(*args, **kwargs)
        self.fields['usuario'].queryset = UserProfile.objects.all()  # Muestra todos los usuarios
        self.fields['equipo'].queryset = Equipo.objects.all()  # Muestra todos los equipos
        self.fields['usuario'].queryset = get_user_model().objects.filter(id=self.initial.get('usuario', None))
        self.fields['encargado'].queryset = UserProfile.objects.filter(rol__nombre='Técnico')  # Muestra todos los roles
        




# Formulario para editar un ticket

class TicketFormEdit(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['titulo', 'descripcion', 'prioridad', 'categoria', 'fecha_resolucion', 'estado']  # Cambia 'fecha' a 'fecha_resolucion'
        labels = {
            'titulo': 'Título',
            'descripcion': 'Descripción',
            'prioridad': 'Prioridad',
            'categoria': 'Categoría',
            'fecha_resolucion': 'Fecha de Resolución',  # Agrega una etiqueta para el nuevo campo
            'estado': 'Estado'
        }
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
            'prioridad': forms.Select(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'fecha_resolucion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),  # Agrega el widget de fecha
            'estado': forms.Select(attrs={'class': 'form-control'}),
        }
# Formulario para registrar un usuario

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    rol = forms.ModelChoiceField(queryset=Rol.objects.all(), required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'rol']
        labels = {
            'username': 'Nombre de usuario',
            'email': 'Correo electrónico',
            'first_name': 'Nombre',
            'last_name': 'Apellidos',
            'password1': 'Contraseña',
            'password2': 'Confirmar contraseña',
            'rol': 'Rol'
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
            'rol': forms.Select(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        user = super(CustomUserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
            UserProfile.objects.create(user=user, rol=self.cleaned_data['rol'], 
                                       nombre=user.first_name, 
                                       apellidos=user.last_name)  # Crear perfil de usuario
        return user




# Formulario para iniciar sesión

class LoginForm(forms.Form):
    username = forms.CharField(label='Nombre de usuario', max_length=150)
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)


class EquipoForm(forms.ModelForm):
    class Meta:
        model = Equipo
        fields = ['nombre', 'descripcion', 'fecha_adquisicion', 'estado', 'marca', 'modelo', 'numero_serie', 'categoria', 'ubicacion', 'fecha_ultimo_mantenimiento', 'proximo_mantenimiento']
        labels = {
            'nombre': 'Nombre del Aparato',
            'descripcion': 'Descripción',
            'fecha_adquisicion': 'Fecha de Adquisición',
            'estado': 'Estado',
            'marca': 'Marca',
            'modelo': 'Modelo',
            'numero_serie': 'Número de Serie',
            'categoria': 'Categoría',
            'ubicacion': 'Ubicación',
            'fecha_ultimo_mantenimiento': 'Último Mantenimiento',
            'proximo_mantenimiento': 'Próximo Mantenimiento',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
            'fecha_adquisicion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'marca': forms.TextInput(attrs={'class': 'form-control'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_serie': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.TextInput(attrs={'class': 'form-control'}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_ultimo_mantenimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'proximo_mantenimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }