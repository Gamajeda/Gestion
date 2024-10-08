from django import forms
from .models import Ticket, Categoria, UserProfile
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

# Formulario para crear una categoría
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
        fields = ['titulo', 'descripcion', 'prioridad', 'categoria', 'fecha_creacion', 'fecha_resolucion', 'usuario']
        labels = {
            'titulo': 'Título',
            'descripcion': 'Descripción',
            'prioridad': 'Prioridad',
            'categoria': 'Categoría',
            'fecha_creacion': 'Fecha de Creación',
            'fecha_resolucion': 'Fecha de Resolución',
            'usuario': 'Usuario',
        }
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
            'prioridad': forms.Select(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'fecha_creacion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_resolucion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'usuario': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(TicketForm, self).__init__(*args, **kwargs)
        self.fields['usuario'].queryset = User.objects.all()  # Cambia aquí para que use User

# Formulario para editar un ticket

class TicketFormEdit(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['titulo', 'descripcion', 'prioridad', 'categoria', 'estado']
        labels = {
            'titulo': 'Título',
            'descripcion': 'Descripción',
            'prioridad': 'Prioridad',
            'categoria': 'Categoría',
            'estado': 'Estado'
        }
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
            'prioridad': forms.Select(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'})
        }
# Formulario para registrar un usuario

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
        labels = {
            'username': 'Nombre de usuario',
            'email': 'Correo electrónico',
            'first_name': 'Nombre',
            'last_name': 'Apellidos',
            'password1': 'Contraseña',
            'password2': 'Confirmar contraseña'
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'})
        }
        
# Formulario para iniciar sesión

class LoginForm(forms.Form):
    username = forms.CharField(label='Nombre de usuario', max_length=150)
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
