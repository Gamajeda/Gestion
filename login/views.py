from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomUserCreationForm, LoginForm, TicketForm, TicketFormEdit, CategoriaForm, EquipoForm, ProblemaFrecuenteForm
from django.contrib.auth import login as django_login, authenticate
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import logout as django_logout, get_user_model

from .models import Categoria, Ticket, UserProfile, Rol, Equipo, ProblemaFrecuente
from django.views.decorators.csrf import csrf_protect

# Vista para la página principal

def agregar_problema(request):
    if request.method == 'POST':
        form = ProblemaFrecuenteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Problema frecuente agregado exitosamente.')
            return redirect('agregar_problema')  # Redirige a la misma página o a una página de éxito
    else:
        form = ProblemaFrecuenteForm()

    return render(request, 'agregar_problema.html', {'form': form})

    

def problemas(request):
    problemas = ProblemaFrecuente.objects.all()
    
    # Verifica si el usuario tiene un perfil y está autenticado
    user_profile = None
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)  # Obtener el perfil del usuario actual
        except UserProfile.DoesNotExist:
            pass  # Maneja el caso en el que el perfil no exista
    
    return render(request, 'preguntas.html', {
        'FAQ': problemas,
        'user_profile': user_profile
    })

def edit_ticket(request, id):
    ticket = get_object_or_404(Ticket, id_ticket=id)  # Obtiene el ticket por ID

    if request.method == 'POST':
        form = TicketFormEdit(request.POST, instance=ticket)
        if form.is_valid():
            form.save()
            return redirect('inicio')  # Redirige a la página de inicio u otra que desees
    else:
        form = TicketFormEdit(instance=ticket)  # Carga el formulario con la instancia del ticket

    return render(request, 'editar_ticket.html', {'form': form, 'ticket': ticket})

# Vista para eliminar un ticket
def delete_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id_ticket=ticket_id)  # Obtiene el ticket
    if request.method == 'POST':
        ticket.delete()  # Elimina el ticket
        messages.success(request, 'Ticket eliminado exitosamente.')
        return redirect('inicio')  # Redirige a la lista de tickets
    return render(request, 'confirmar_eliminar.html', {'ticket': ticket})



def index(request):
    return render(request, 'index.html')

def categoria(request):
     # Verifica si el usuario tiene un perfil y está autenticado
    user_profile = None
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)  # Obtener el perfil del usuario actual
        except UserProfile.DoesNotExist:
            pass  # Maneja el caso en el que el perfil no exista
    
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría creada exitosamente.')
            return redirect('categoria')  # Cambia esto según la ruta a la que quieras redirigir
    else:
        form = CategoriaForm()
    return render(request, 'crear_categoria.html', {'form': form, 'user_profile': user_profile})

def ticket_list(request):
    tickets = Ticket.objects.all()  # Obtén todos los tickets
    return render(request, 'inicio.html', {'tickets': tickets})  # Pasa los tickets al template
 # Pasa los tickets al template

# Vista para la página de inicio
@csrf_protect
def inicio(request):
    search_query = request.GET.get('buscar', '').strip()  # Obtiene el término de búsqueda y elimina espacios
    tickets = Ticket.objects.filter(estado='P')  # Solo tickets pendientes

    # Si hay un término de búsqueda, filtra los tickets
    if search_query:
        tickets = tickets.filter(
            Q(usuario__user__username__icontains=search_query) |  # Filtra por nombre de usuario
            Q(titulo__icontains=search_query) |  # Filtra por título
            Q(descripcion__icontains=search_query)  # Filtra por descripción
        ).distinct()  # Asegúrate de que no haya duplicados

    # Intenta obtener el perfil del usuario actual
    try:
        user_profile = UserProfile.objects.get(user=request.user)  # Asume que hay un único perfil
    except UserProfile.DoesNotExist:
        user_profile = None  # Maneja el caso donde no hay perfil
    except UserProfile.MultipleObjectsReturned:
        user_profile = None  # Maneja el caso de duplicados (esto es un error)

    return render(request, 'inicio.html', {
        'tickets': tickets,  # Ahora solo hay tickets pendientes
        'user_profile': user_profile,
    })


def crear_equipo(request):
     # Verifica si el usuario tiene un perfil y está autenticado
    user_profile = None
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)  # Obtener el perfil del usuario actual
        except UserProfile.DoesNotExist:
            pass  # Maneja el caso en el que el perfil no exista
    
    if request.method == 'POST':
        form = EquipoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Aparato creado exitosamente.')
            return redirect('crear_equipo')  # Redirige a la vista deseada
    else:
        form = EquipoForm()

    return render(request, 'crear_equipo.html', {'form': form, 'user_profile': user_profile})


def todo(request):
    search_query = request.GET.get('buscar', '')  # Obtiene el término de búsqueda
    tickets = Ticket.objects.filter(estado='R')  # Solo tickets pendientes

    # Si hay un término de búsqueda, filtra los tickets
    if search_query:
        tickets = tickets.filter(
            Q(usuario__user__username__icontains=search_query) |  # Asegúrate de usar el campo correcto
            Q(titulo__icontains=search_query) |  # Filtra por título
            Q(descripcion__icontains=search_query)  # Filtra por descripción
        )

    # Intenta obtener el perfil del usuario actual
    try:
        user_profile = UserProfile.objects.get(user=request.user)  # Asume que hay un único perfil
    except UserProfile.DoesNotExist:
        user_profile = None  # Maneja el caso donde no hay perfil
    except UserProfile.MultipleObjectsReturned:
        user_profile = None  # Maneja el caso de duplicados (esto es un error)

    return render(request, 'inicio.html', {
        'tickets': tickets,  # Ahora solo hay tickets pendientes
        'user_profile': user_profile,
    })




# Vista para la página de tickets
@csrf_protect
def tikcet(request):

     # Verifica si el usuario tiene un perfil y está autenticado
    user_profile = None
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)  # Obtener el perfil del usuario actual
        except UserProfile.DoesNotExist:
            pass  # Maneja el caso en el que el perfil no exista
    
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            try:
                usuario_perfil = UserProfile.objects.get(user=request.user)
                ticket.usuario = usuario_perfil  # Asignar el perfil de usuario como creador
            except UserProfile.DoesNotExist:
                messages.error(request, 'Error: el perfil de usuario no se encuentra.')
                return redirect('tikcet')

            ticket.save()  # Guardar el ticket

            messages.success(request, 'Ticket creado exitosamente.')
            return redirect('inicio')  # Cambiar a 'inicio' en vez de 'ticket_view'
            
    else:
        form = TicketForm()

    # Obtener todas las categorías de la base de datos
    categorias = Categoria.objects.all()
    
    # Filtrar las categorías cuyo término tiene 5 letras o menos
    categorias = [cat for cat in categorias if len(cat.termino) <= 5]

    return render(request, 'crear_ticket.html', {'form': form, 'categorias': categorias, 'user_profile': user_profile})

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
     # Verifica si el usuario tiene un perfil y está autenticado
    user_profile = None
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)  # Obtener el perfil del usuario actual
        except UserProfile.DoesNotExist:
            pass  # Maneja el caso en el que el perfil no exista
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Crear el usuario
            user = form.save()
            # Obtener el rol (puedes cambiar esto según cómo obtienes el rol)
            rol_id = request.POST.get('rol_id')  # Asegúrate de que este campo esté en tu formulario
            if rol_id:
                rol = Rol.objects.get(id=rol_id)
                user.roles.add(rol)  # Asigna el rol al usuario
            
            messages.success(request, 'Usuario creado exitosamente.')

            form = CustomUserCreationForm()
              # Redirigir después de crear el usuario
    else:
        form = CustomUserCreationForm()

    return render(request, 'register.html', {'form': form, 'user_profile': user_profile})