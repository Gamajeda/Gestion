from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomUserCreationForm, LoginForm, TicketForm, TicketFormEdit, CategoriaForm
from django.contrib.auth import login as django_login, authenticate
from django.contrib import messages
from django.contrib.auth import logout as django_logout, get_user_model
from .models import Categoria, Ticket
from django.views.decorators.csrf import csrf_protect

# Vista para la página principal
def edit_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if request.method == 'POST':
        form = TicketForm(request.POST, instance=ticket)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ticket editado exitosamente.')
            return redirect('inicio')
    else:
        form = TicketForm(instance=ticket)
    return render(request, 'editar_ticket.html', {'form': form, 'ticket': ticket})

# Vista para eliminar un ticket
def delete_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)  # Obtiene el ticket
    if request.method == 'POST':
        ticket.delete()  # Elimina el ticket
        messages.success(request, 'Ticket eliminado exitosamente.')
        return redirect('inicio')  # Redirige a la lista de tickets
    return render(request, 'confirmar_eliminar.html', {'ticket': ticket})



def index(request):
    return render(request, 'index.html')

def categoria(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría creada exitosamente.')
            return redirect('categoria')  # Cambia esto según la ruta a la que quieras redirigir
    else:
        form = CategoriaForm()
    return render(request, 'crear_categoria.html', {'form': form})

def ticket_list(request):
    tickets = Ticket.objects.all()  # Obtén todos los tickets
    return render(request, 'inicio.html', {'tickets': tickets})  # Pasa los tickets al template
 # Pasa los tickets al template

# Vista para la página de inicio
@csrf_protect
def inicio(request):
    tickets = Ticket.objects.all()  # Obtiene todos los tickets
    return render(request, 'inicio.html', {'tickets': tickets})  # Pasa los tickets al template


# Vista para la página de tickets
def tikcet(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ticket creado exitosamente.')
            return redirect('tikcet')  # Cambia esto según la ruta a la que quieras redirigir
    else:
        form = TicketForm()

    # Obtener todas las categorías de la base de datos
    categorias = Categoria.objects.all()
    
    # Filtrar las categorías cuyo término tiene 5 letras o menos
    categorias = [cat for cat in categorias if len(cat.termino) <= 5]
    
    User = get_user_model()  # Obtener el modelo de usuario
    usuarios = User.objects.all()  # Obtener todos los usuarios
    
     # Pasar los usuarios al formulario
    form.fields['usuario'].queryset = usuarios  # Esto asigna la lista de usuarios al campo de usuario


    return render(request, 'crear_ticket.html', {'form': form, 'categorias': categorias, 'usuarios': usuarios})

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
