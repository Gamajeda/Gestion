from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomUserCreationForm, LoginForm, TicketForm, TicketFormEdit, CategoriaForm, EquipoForm, ProblemaFrecuenteForm, UserProfileForm
from django.contrib.auth import login as django_login, authenticate, update_session_auth_hash
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import logout as django_logout, get_user_model
from django.utils import timezone
from .models import Categoria, Ticket, UserProfile, Rol, Equipo, ProblemaFrecuente
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm

# Vista para la página principal

@login_required
def editar_perfil(request):
    user_profile = UserProfile.objects.get(user=request.user)
    
    if request.method == 'POST':
        if 'foto' in request.POST or 'foto' in request.FILES:
            profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Tu perfil ha sido actualizado exitosamente.')
                return redirect('perfil')
        elif 'old_password' in request.POST:
            password_form = PasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # Mantiene al usuario autenticado después de cambiar la contraseña
                messages.success(request, 'Tu contraseña ha sido actualizada exitosamente.')
                return redirect('perfil')
    else:
        profile_form = UserProfileForm(instance=user_profile)
        password_form = PasswordChangeForm(user=request.user)
    
    return render(request, 'editar_perfil.html', {
        'profile_form': profile_form,
        'password_form': password_form,
        'user_profile': user_profile
    })

@login_required
def perfil(request):
    user_profile = UserProfile.objects.get(user=request.user)
    
    profile_form = UserProfileForm(instance=user_profile)
    password_form = PasswordChangeForm(user=request.user)
    
    return render(request, 'perfil.html', {
        'profile_form': profile_form,
        'password_form': password_form,
        'user_profile': user_profile
    })

def calificar_trabajo(request, id):
    ticket = get_object_or_404(Ticket, id_ticket=id)
    
    # Verificar si el usuario actual es el creador del ticket
    if ticket.usuario != request.user.userprofile:
        messages.error(request, 'No tienes permiso para calificar este ticket.')
        return redirect('inicio')
    
    # Verificar si el ticket ya ha sido calificado
    if ticket.calificacion is not None:
        messages.info(request, 'Este ticket ya ha sido calificado.')
        return redirect('inicio')
    
    if request.method == 'POST':
        calificacion = request.POST.get('calificacion')
        if calificacion:
            ticket.calificacion = int(calificacion)
            ticket.save()
            messages.success(request, 'Gracias por calificar el trabajo.')
            return redirect('inicio')  # Redirige a la página de inicio después de calificar
    return render(request, 'calificar_trabajo.html', {'ticket': ticket})
def all(request):
    search_query = request.GET.get('buscar', '')  # Obtiene el término de búsqueda
    user_profile = UserProfile.objects.get(user=request.user)
    if user_profile.rol.nombre == 'Cliente':
        tickets = Ticket.objects.filter(usuario=user_profile) # Solo tickets pendientes
    elif user_profile.rol.nombre == 'Técnico':
        tickets = Ticket.objects.filter(encargado=user_profile)
    else:
        tickets = Ticket.objects.all()

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

def menu(request):
    user_profile = None
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            pass  # Maneja el caso en el que el perfil no exista

    return render(request, 'menu.html', {
        'user_profile': user_profile
    })

def detalle_problema(request, id):
    problema = get_object_or_404(ProblemaFrecuente, id=id)
    
    if request.method == 'POST':
        calificacion = request.POST.get('calificacion')
        if calificacion:
            problema.calificacion = int(calificacion)
            problema.save()
            messages.success(request, 'Calificación guardada exitosamente.')
            return redirect('detalle_problema', id=id)
    
    user_profile = UserProfile.objects.get(user=request.user)
    return render(request, 'detalle_problema.html', {
        'problema': problema,
        'user_profile': user_profile
    })

def editar_problema(request, id):
    problema = get_object_or_404(ProblemaFrecuente, id=id)
    if request.method == 'POST':
        form = ProblemaFrecuenteForm(request.POST, instance=problema)
        if form.is_valid():
            form.save()
            messages.success(request, 'El problema ha sido actualizado exitosamente.')
            return redirect('preguntas')
    else:
        form = ProblemaFrecuenteForm(instance=problema)
    return render(request, 'editar_problema.html', {'form': form})

def eliminar_problema(request, id):
    problema = get_object_or_404(ProblemaFrecuente, id=id)
    if request.method == 'POST':
        problema.delete()
        messages.success(request, 'El problema ha sido eliminado exitosamente.')
        return redirect('preguntas')
    return render(request, 'confirmar_eliminar_problema.html', {'problema': problema})

def ticket_detail(request, id):
    ticket = get_object_or_404(Ticket, id_ticket=id)  # Obtiene el ticket por ID
    user_profile = UserProfile.objects.get(user=request.user)
    
    # Verifica si el usuario es administrador o técnico
    is_admin = user_profile.rol.nombre == 'Administrador'
    is_technician = user_profile.rol.nombre == 'Técnico'

    return render(request, 'ticket.html', {
        'ticket': ticket,
        'is_admin': is_admin,
        'is_technician': is_technician
    })

def editar_ticket(request, id):
    ticket = get_object_or_404(Ticket, id_ticket=id)
    if request.method == 'POST':
        form = TicketFormEdit(request.POST, instance=ticket)
        if form.is_valid():
            ticket = form.save(commit=False)
            if ticket.estado == 'R':  # Si el ticket se marca como resuelto
                ticket.fecha_resolucion = timezone.now()  # Establece la fecha de resolución
                ticket.save()
                messages.success(request, 'El ticket ha sido actualizado exitosamente.')
                return redirect('calificar_trabajo', id=id)  # Redirige a la página de calificación
            ticket.save()
            messages.success(request, 'El ticket ha sido actualizado exitosamente.')
            return redirect('ticket_detail', id=id)
    else:
        form = TicketFormEdit(instance=ticket)
    return render(request, 'editar_ticket.html', {'form': form})

def eliminar_ticket(request, id):
    ticket = get_object_or_404(Ticket, id_ticket=id)
    if request.method == 'POST':
        ticket.delete()
        messages.success(request, 'El ticket ha sido eliminado exitosamente.')
        return redirect('inicio')  # Redirige a la lista de tickets o a otra página
    return render(request, 'confirmar_eliminar.html', {'ticket': ticket})



def agregar_problema(request):
    if request.method == 'POST':
        form = ProblemaFrecuenteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Problema frecuente agregado exitosamente.')
            return redirect('preguntas')  # Redirige a la misma página o a una página de éxito
    else:
        form = ProblemaFrecuenteForm()

    return render(request, 'agregar_problema.html', {'form': form})

    

def preguntas(request):
    problemas = ProblemaFrecuente.objects.all()
    user_profile = UserProfile.objects.get(user=request.user)
    return render(request, 'preguntas.html', {
        'problemas': problemas,
        'user_profile': user_profile
    })

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
    user_profile = UserProfile.objects.get(user=request.user)
    
    # Verificar si hay tickets resueltos sin calificar para el usuario actual
    tickets_sin_calificar = Ticket.objects.filter(usuario=user_profile, estado='R', calificacion__isnull=True)
    if tickets_sin_calificar.exists():
        return redirect('calificar_trabajo', id=tickets_sin_calificar.first().id_ticket)
    
    if user_profile.rol.nombre == 'Cliente':
        tickets = Ticket.objects.filter(usuario=user_profile, estado='P')
    elif user_profile.rol.nombre == 'Técnico':
        tickets = Ticket.objects.filter(encargado=user_profile, estado='P')
    else:
        tickets = Ticket.objects.filter(estado='P')
    
    search_query = request.GET.get('buscar', '')
    if search_query:
        tickets = tickets.filter(
            Q(usuario__user__username__icontains=search_query) |
            Q(titulo__icontains=search_query) |
            Q(descripcion__icontains=search_query)
        )
    
    return render(request, 'inicio.html', {
        'tickets': tickets,
        'user_profile': user_profile
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
            return redirect('inicio')  # Redirige a la vista deseada
    else:
        form = EquipoForm()

    return render(request, 'crear_equipo.html', {'form': form, 'user_profile': user_profile})


def todo(request):
    search_query = request.GET.get('buscar', '')  # Obtiene el término de búsqueda
    user_profile = UserProfile.objects.get(user=request.user)
    
    if user_profile.rol.nombre == 'Cliente':
        tickets = Ticket.objects.filter(usuario=user_profile, estado='R')
    elif user_profile.rol.nombre == 'Técnico':
        tickets = Ticket.objects.filter(encargado=user_profile, estado='R')
    else:
        tickets = Ticket.objects.filter(estado='R')
    
    # Si hay un término de búsqueda, filtra los tickets
    if search_query:
        tickets = tickets.filter(
            Q(usuario__user__username__icontains=search_query) |
            Q(titulo__icontains=search_query) |
            Q(descripcion__icontains=search_query)
        )
    
    return render(request, 'inicio.html', {
        'tickets': tickets,
        'user_profile': user_profile
    })




# Vista para la página de tickets
@csrf_protect
def tikcet(request):
    if request.method == 'POST':
        form = TicketForm(request.POST, user=request.user)
        if form.is_valid():
            ticket = form.save(commit=False)
            if not request.user.is_staff:  # Si el usuario no es administrador
                ticket.estado = 'P'
                ticket.prioridad = ''
                ticket.encargado = None  # O establece un valor predeterminado si es necesario
            ticket.categoria = Categoria.objects.get(nombre='General')  # Establece la categoría predeterminada
            ticket.save()
            messages.success(request, 'Tu ticket ha sido creado exitosamente.')
            return redirect('inicio')  # Redirige a la página de inicio
    else:
        form = TicketForm(user=request.user)

    # Obtener todas las categorías de la base de datos
    categorias = Categoria.objects.all()
    
    # Filtrar las categorías cuyo término tiene 5 letras o menos
    categorias = [cat for cat in categorias if len(cat.termino) <= 5]

    return render(request, 'crear_ticket.html', {'form': form, 'categorias': categorias})

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
                return redirect('menu')
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