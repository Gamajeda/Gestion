from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm, LoginForm
from django.contrib.auth import login as django_login, authenticate
from django.contrib import messages
from django.contrib.auth import logout as django_logout
from django.views.decorators.csrf import csrf_protect

# Vista para la página principal
def index(request):
    return render(request, 'index.html')


# Vista para la página de inicio
@csrf_protect
def inicio(request):
    return render(request, 'inicio.html')

# Vista para la página de tickets
def tikcet(request):
    return render(request, 'crear_ticket.html')


# Vista para iniciar sesión
def login_view(request):
    form = LoginForm()  # Asegúrate de que estés instanciando el formulario
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                django_login(request, user)
                return redirect('inicio')
            else:
                messages.error(request, 'Usuario o contraseña incorrectos')
    return render(request, 'login.html', {'form': form})



# Vista para cerrar sesión
def logout(request):
    django_logout(request)
    return redirect('login')

# Vista para registrar un usuario
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            django_login(request, user)  # Inicia sesión al nuevo usuario
            return redirect('inicio')  # Cambia esto si quieres redirigir a otra vista
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})
