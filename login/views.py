from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomUserCreationForm, LoginForm, TicketForm, TicketFormEdit, CategoriaForm, EquipoForm, ProblemaFrecuenteForm, UserProfileForm, CalificacionForm
from django.contrib.auth import login as django_login, authenticate, update_session_auth_hash
from django.db.models import Q
from django.contrib import messages
from datetime import datetime
import json
from django.db.models.functions import ExtractMonth
from django.contrib.auth import logout as django_logout, get_user_model
from django.utils import timezone
from django.db.models import Count
from .models import Categoria, Ticket, UserProfile, Rol, Equipo, ProblemaFrecuente, Calificacion
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.http import JsonResponse
from django.db import models  # Importa models
# Vista para la página principal

def graficas(request):
    # Obtener el año actual
    current_year = datetime.now().year

    # Obtener todos los perfiles de usuario
    usuarios = UserProfile.objects.all()

    # Obtener el perfil de usuario seleccionado
    usuario_id = request.GET.get('usuario')
    if usuario_id:
        user_profile = UserProfile.objects.get(id=usuario_id)
    else:
        user_profile = request.user.userprofile

    # Obtener los datos de tickets creados, resueltos y pendientes por mes para el usuario seleccionado
    tickets_creados = Ticket.objects.filter(fecha_creacion__year=current_year, usuario=user_profile).annotate(month=ExtractMonth('fecha_creacion')).values('month').annotate(count=Count('id_ticket')).order_by('month')
    tickets_resueltos = Ticket.objects.filter(fecha_resolucion__year=current_year, estado='R', encargado=user_profile).annotate(month=ExtractMonth('fecha_resolucion')).values('month').annotate(count=Count('id_ticket')).order_by('month')
    tickets_pendientes = Ticket.objects.filter(fecha_creacion__year=current_year, estado='P', usuario=user_profile).annotate(month=ExtractMonth('fecha_creacion')).values('month').annotate(count=Count('id_ticket')).order_by('month')

    # Crear listas para los datos
    labels = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    data_creados = [0] * 12
    data_resueltos = [0] * 12
    data_pendientes = [0] * 12

    for ticket in tickets_creados:
        data_creados[ticket['month'] - 1] = ticket['count']

    for ticket in tickets_resueltos:
        data_resueltos[ticket['month'] - 1] = ticket['count']

    for ticket in tickets_pendientes:
        data_pendientes[ticket['month'] - 1] = ticket['count']

    return render(request, 'graficas.html', {
        'usuarios': usuarios,
        'selected_usuario': user_profile,
        'labels': labels,
        'data_creados': data_creados,
        'data_resueltos': data_resueltos,
        'data_pendientes': data_pendientes,
    })


@login_required
def calificar_problema(request, id):
    problema = get_object_or_404(ProblemaFrecuente, id=id)
    usuario = request.user
    user_profile = UserProfile.objects.get(user=request.user)

    if request.method == 'POST':
        form = CalificacionForm(request.POST)
        if form.is_valid():
            calificacion = form.save(commit=False)
            calificacion.problema = problema
            calificacion.usuario = usuario
            calificacion.save()

            # Actualizar el promedio de calificaciones
            calificaciones = Calificacion.objects.filter(problema=problema)
            promedio = calificaciones.aggregate(models.Avg('calificacion'))['calificacion__avg']
            problema.promedio_calificacion = promedio
            problema.save()

            messages.success(request, 'Gracias por calificar el problema.')
            return redirect('detalle_problema', id=id)
    else:
        form = CalificacionForm()

    return render(request, 'calificar_problema.html', {'form': form, 'problema': problema, 'user_profile': user_profile})

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


@login_required
def calificar_trabajo(request, id):
    ticket = get_object_or_404(Ticket, id_ticket=id)
    user = request.user

    # Verificar si el usuario actual es el creador del ticket
    if ticket.usuario.user.id != user.id:
        messages.error(request, 'No puedes calificar un ticket que no te pertenece.')
        print("paso0")
        return redirect('inicio')

    if request.method == 'POST':
        if 'calificacion' in request.POST:
            print("Datos del formulario POST:", request.POST)
            form = CalificacionForm(request.POST)
            print("paso1")
            if form.is_valid():
                calificacion = form.cleaned_data['calificacion']
                if not calificacion:  # Verifica si la calificación es vacía
                    messages.error(request, 'Por favor, selecciona una calificación.')
                    return render(request, 'calificar_trabajo.html', {'ticket': ticket, 'form': form})
                
                ticket.calificacion = calificacion
                ticket.save()
                messages.success(request, 'El ticket ha sido calificado exitosamente.')
                return redirect('inicio')


            else:
                print("Errores del formulario:", form.errors)
        elif 'no_completado' in request.POST:
            print("paso3")
            ticket.estado = 'P'  # Cambia el estado a 'Pendiente'
            ticket.save()
            messages.success(request, 'El estado del ticket ha sido cambiado a Pendiente.')
            return redirect('inicio')  # Redirigir al inicio después de cambiar el estado

    form = CalificacionForm()
    return render(request, 'calificar_trabajo.html', {'ticket': ticket, 'form': form})








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
    usuario = request.user
    calificacion_usuario = None

    if request.user.is_authenticated:
        calificacion_usuario = Calificacion.objects.filter(problema=problema, usuario=usuario).first()

    if request.method == 'POST' and not calificacion_usuario:
        form = CalificacionForm(request.POST)
        if form.is_valid():
            calificacion = form.save(commit=False)
            calificacion.problema = problema
            calificacion.usuario = usuario
            calificacion.save()

            # Actualizar el promedio de calificaciones
            calificaciones = Calificacion.objects.filter(problema=problema)
            promedio = calificaciones.aggregate(models.Avg('calificacion'))['calificacion__avg']
            problema.promedio_calificacion = promedio
            problema.save()

            messages.success(request, 'Gracias por calificar el problema.')
            return redirect('detalle_problema', id=id)
    else:
        form = CalificacionForm()

    return render(request, 'detalle_problema.html', {
        'problema': problema,
        'form': form,
        'calificacion_usuario': calificacion_usuario,
        'user_profile': UserProfile.objects.get(user=request.user)
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
    ticket = get_object_or_404(Ticket, id_ticket=id)  # Obtienes el ticket
    user_profile = UserProfile.objects.get(user=request.user)  # Obtienes el perfil del usuario
    estrellas = range(1, 6)  # Rango de estrellas para la calificación (1 a 5)

    return render(request, 'ticket.html', {
        'ticket': ticket, 
        'user_profile': user_profile,
        'estrellas': estrellas,  # Pasamos el rango de estrellas a la plantilla
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
@login_required
def inicio(request):
    user_profile = UserProfile.objects.get(user=request.user)

    # Actualiza los tickets con calificación vacía a None directamente en la base de datos
    Ticket.objects.filter(calificacion='0').update(calificacion=None)

    # Verificar si hay tickets resueltos sin calificar para el usuario actual
    tickets_sin_calificar = Ticket.objects.filter(calificacion__isnull=True)
    
    # Depuración: Imprimir los tickets sin calificar
    print(tickets_sin_calificar)

    if tickets_sin_calificar.exists():
        # Si existen tickets sin calificar, redirigir a la página de calificación del primero
        ticket_a_calificar = tickets_sin_calificar.first()  # Obtiene el primer ticket sin calificar
        return redirect('calificar_trabajo', id=ticket_a_calificar.id_ticket)
    
    # Si no hay tickets sin calificar, seguir con el flujo normal
    if user_profile.rol.nombre == 'Cliente':
        tickets = Ticket.objects.filter(usuario=user_profile, estado='R')
    elif user_profile.rol.nombre == 'Técnico':
        tickets = Ticket.objects.filter(encargado=user_profile, estado='R')
    else:
        tickets = Ticket.objects.filter(estado='R')

    # Búsqueda
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
        tickets = Ticket.objects.filter(usuario=user_profile, estado='P')
    elif user_profile.rol.nombre == 'Técnico':
        tickets = Ticket.objects.filter(encargado=user_profile, estado='P')
    else:
        tickets = Ticket.objects.filter(estado='P')
    
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