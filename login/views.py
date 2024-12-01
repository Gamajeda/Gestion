from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomUserCreationForm, LoginForm, TicketForm, TicketFormEdit, CategoriaForm, EquipoForm, ProblemaFrecuenteForm, UserProfileForm, CalificacionForm, EmailChangeForm
from django.contrib.auth import login as django_login, authenticate, update_session_auth_hash
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from django.core.mail import send_mail
from django.db.models import Q
from django.contrib import messages
from datetime import datetime, timedelta
import json
from collections import Counter
from django.db.models.functions import ExtractMonth,TruncYear
from django.contrib.auth import logout as django_logout, get_user_model
from django.utils import timezone
from django.utils.timezone import localtime
from django.utils.crypto import get_random_string
from django.db.models import Count
from .models import Categoria, Ticket, UserProfile, Rol, Equipo, ProblemaFrecuente, Calificacionproblema, Calificaciontrabajo, HistorialTecnico, Invitacion
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.http import JsonResponse,HttpResponse
from django.db.models import Avg
from .decorators import admin_required
from django.db import models  # Importa models
# Vista para la página principal


@login_required
def descargar_ticket(request, id):
    # Obtener el ticket específico
    ticket = get_object_or_404(Ticket, id_ticket=id)

    # Crear un buffer en memoria para guardar el PDF
    buffer = BytesIO()

    # Crear un objeto canvas que genera el PDF
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter  # Medidas de la página (Carta: 8.5x11 pulgadas)

    # Título del PDF
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, height - 40, f"Ticket #{ticket.id_ticket}")

    # Añadir detalles del ticket
    p.setFont("Helvetica", 12)
    p.drawString(100, height - 60, f"Título: {ticket.titulo}")
    p.drawString(100, height - 80, f"Descripción: {ticket.descripcion}")
    p.drawString(100, height - 100, f"Prioridad: {ticket.get_prioridad_display()}")
    p.drawString(100, height - 120, f"Estado: {ticket.get_estado_display()}")
    p.drawString(100, height - 140, f"Fecha de Creación: {ticket.fecha_creacion}")

    # Historial de técnicos
    p.drawString(100, height - 160, "Historial de Técnicos:")
    y_position = height - 180  # Posición inicial para los técnicos
    for historial_item in HistorialTecnico.objects.filter(ticket=ticket):
        p.drawString(100, y_position, f"Técnico: {historial_item.tecnico.user.username} - Fecha: {historial_item.fecha_cambio}")
        if historial_item.motivo:
            p.drawString(100, y_position - 20, f"Motivo: {historial_item.motivo}")
        y_position -= 40  # Ajustar espacio entre técnicos

    # Guardar el PDF en el buffer
    p.showPage()
    p.save()

    # Mover el buffer a una posición inicial
    buffer.seek(0)

    # Crear una respuesta HTTP que permita descargar el archivo PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ticket_{ticket.id_ticket}.pdf"'

    # Escribir el contenido del buffer en la respuesta
    response.write(buffer.getvalue())

    return response



@login_required
@admin_required
def graficas(request):
    # Obtener todos los perfiles de usuario
    usuarios = UserProfile.objects.all()

    # Obtener el id del usuario seleccionado desde el GET request
    usuario_id = request.GET.get('usuario')
    
    if usuario_id:
        user_profile = UserProfile.objects.get(id=usuario_id)
    else:
        user_profile = request.user.userprofile  # Si no se selecciona un usuario, usar el del usuario logueado

    # Obtener el rol del usuario seleccionado
    rol_usuario = user_profile.rol  # Suponiendo que el campo 'rol' existe en UserProfile

    # Obtener los tickets relacionados con el usuario seleccionado
    tickets_creados = Ticket.objects.filter(fecha_creacion__year=datetime.now().year, usuario=user_profile).count()
    tickets_resueltos = Ticket.objects.filter(fecha_resolucion__year=datetime.now().year, estado='R', encargado=user_profile).count()
    tickets_pendientes = Ticket.objects.filter(fecha_creacion__year=datetime.now().year, estado='P', usuario=user_profile).count()

    # Crear listas para los datos
    labels = ['Tickets Creados', 'Tickets Resueltos', 'Tickets Pendientes']
    data_creados = [tickets_creados]
    data_resueltos = [tickets_resueltos]
    data_pendientes = [tickets_pendientes]

    # Generar el contexto para las gráficas
    context = {
        'usuarios': usuarios,
        'selected_usuario': user_profile,
        'rol_usuario': rol_usuario,  # Incluir el rol en el contexto
        'labels': labels,
        'data_creados': data_creados,
        'data_resueltos': data_resueltos,
        'data_pendientes': data_pendientes,
    }

    return render(request, 'graficas.html', context)

@login_required
@login_required
def detalle_problema(request, id):
    problema = get_object_or_404(ProblemaFrecuente, id=id)
    usuario = request.user
    user_profile = UserProfile.objects.get(user=request.user)

    calificaciones_usuario = Calificacionproblema.objects.filter(problema=problema, usuario=usuario)
    if calificaciones_usuario.exists():
        calificacion = calificaciones_usuario.first().calificacion
        form = None
    else:
        if request.method == 'POST':
            form = CalificacionForm(request.POST)
            if form.is_valid():
                calificacion = form.save(commit=False)
                calificacion.problema = problema
                calificacion.usuario = usuario
                calificacion.save()

                # Actualizar el promedio de calificaciones
                calificaciones = Calificacionproblema.objects.filter(problema=problema)
                promedio = calificaciones.aggregate(Avg('calificacion'))['calificacion__avg']
                problema.promedio_calificacion = promedio
                problema.save()

                messages.success(request, 'Gracias por calificar el problema.')
                return redirect('detalle_problema', id=id)
        else:
            form = CalificacionForm()

    return render(request, 'detalle_problema.html', {
        'form': form,
        'problema': problema,
        'user_profile': user_profile,
        'calificado': calificaciones_usuario.exists(),
        'calificacion': calificacion if calificaciones_usuario.exists() else None,
    })


@login_required
def calificar_problema(request, id):
    problema = get_object_or_404(ProblemaFrecuente, id=id)
    usuario = request.user

    if request.method == 'POST':
        calificacion = request.POST.get('calificacion')
        if calificacion:
            # Verificar si ya existe una calificación para este usuario y problema
            calificaciones_usuario = Calificacionproblema.objects.filter(problema=problema, usuario=usuario)
            if not calificaciones_usuario.exists():
                Calificacionproblema.objects.create(problema=problema, usuario=usuario, calificacion=calificacion)
                # Actualizar el promedio de calificaciones
                calificaciones = Calificacionproblema.objects.filter(problema=problema)
                promedio = calificaciones.aggregate(Avg('calificacion'))['calificacion__avg']
                problema.promedio_calificacion = promedio
                problema.save()

                messages.success(request, 'Gracias por calificar el problema.')
            else:
                messages.error(request, 'Ya has calificado este problema.')
            return redirect('detalle_problema', id=id)

    return render(request, 'calificar_problema.html', {'problema': problema})

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
        elif 'email' in request.POST:
            email_form = EmailChangeForm(user=request.user, data=request.POST)
            if email_form.is_valid():
                # Actualiza el correo electrónico del usuario
                user = request.user
                user.email = email_form.cleaned_data['email']
                user.save()
                messages.success(request, 'Tu correo electrónico ha sido actualizado exitosamente.')
                return redirect('perfil')
            else:
                messages.error(request, 'Hubo un error al actualizar tu correo electrónico.')
        elif 'old_password' in request.POST:
            password_form = PasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Tu contraseña ha sido actualizada exitosamente.')
                return redirect('perfil')
            else:
                messages.error(request, 'Hubo un error al actualizar tu contraseña.')
    else:
        profile_form = UserProfileForm(instance=user_profile)
        email_form = EmailChangeForm(user=request.user)
        password_form = PasswordChangeForm(user=request.user)

    return render(request, 'editar_perfil.html', {
        'profile_form': profile_form,
        'email_form': email_form,
        'password_form': password_form,
        'user_profile': user_profile,
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
def inicio(request):
    search_query = request.GET.get('buscar', '')
    user_profile = UserProfile.objects.get(user=request.user)
    Ticket.objects.filter(calificacion='0').update(calificacion=None)
    
    # Filtra los tickets resueltos sin calificación para el usuario actual
    tickets_sin_calificar = Ticket.objects.filter(
        calificacion__isnull=True,  # Calificación vacía
        usuario=user_profile,       # Solo tickets del usuario actual
        estado='R'                  # Opcional: Asegura que el ticket esté resuelto
    )
    
    # Depuración: Imprimir los tickets sin calificar para verificar
    print(tickets_sin_calificar)
    
    # Si existen tickets sin calificar, redirige al usuario para calificar el primero
    if tickets_sin_calificar.exists():
        ticket_a_calificar = tickets_sin_calificar.first()  # Obtiene el primer ticket sin calificar
        return redirect('calificar_trabajo', id=ticket_a_calificar.id_ticket)

    # Si el usuario es Técnico
    

    if user_profile.rol.nombre == 'Técnico':
        # Obtener tickets próximos a vencer
        fecha_actual = timezone.localtime(timezone.now()) 
        fecha_limite = fecha_actual + timedelta(days=3)

        tickets_proximos_a_vencer = Ticket.objects.filter(
            fecha_resolucion__lte=fecha_limite,
            encargado=user_profile,
            estado='P'
        )
    else:
        tickets_proximos_a_vencer = None

    # Obtener los tickets según el rol
    if user_profile.rol.nombre == 'Cliente':
        tickets = Ticket.objects.filter(usuario=user_profile, estado='R')
    elif user_profile.rol.nombre == 'Técnico':
        tickets = Ticket.objects.filter(encargado=user_profile, estado='R')
    else:
        tickets = Ticket.objects.filter(estado='R')

    # Si hay un término de búsqueda

    prioridad_map = {
        'baja': 'B',
        'media': 'M',
        'alta': 'A'
    }

    if search_query:
        tickets = tickets.filter(
            Q(usuario__user__username__icontains=search_query) |
            Q(titulo__icontains=search_query) |
            Q(prioridad__icontains=prioridad_map.get(search_query, search_query))|
            Q(categoria__termino__icontains=search_query)|
            Q(estado__icontains=search_query)|
            Q(encargado__user__username__icontains=search_query)|
            Q(fecha_creacion__icontains=search_query)|
            Q(fecha_resolucion__icontains=search_query)|
            Q(comentarios__icontains=search_query)
        )

    # Depuración
    print(f"Search Query: {search_query}")
    print(f"Tickets encontrados: {tickets.count()}")

    return render(request, 'inicio.html', {
        'tickets': tickets,
        'user_profile': user_profile,
        'calificar_trabajo': calificar_trabajo,
        'tickets_proximos_a_vencer': tickets_proximos_a_vencer,
        'query': search_query
    })

@login_required
def calificar_trabajo(request, id):
    ticket = get_object_or_404(Ticket, id_ticket=id)
    user = request.user
    print("paso0")
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







@login_required
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
    prioridad_map = {
        'Baja': 'B',
        'Media': 'M',
        'Alta': 'A'
    }
    
    # Si hay un término de búsqueda, filtra los tickets
    if search_query:
        tickets = tickets.filter(
            Q(usuario__user__username__icontains=search_query) |
            Q(titulo__icontains=search_query) |
            Q(prioridad__icontains=prioridad_map.get(search_query, search_query))|
            Q(categoria__termino__icontains=search_query)|
            Q(estado__icontains=search_query)|
            Q(encargado__user__username__icontains=search_query)|
            Q(fecha_creacion__icontains=search_query)|
            Q(fecha_resolucion__icontains=search_query)|
            Q(comentarios__icontains=search_query)
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
        'query': search_query
    })

@login_required
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



@login_required
@admin_required
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

@login_required
@admin_required
def eliminar_problema(request, id):
    problema = get_object_or_404(ProblemaFrecuente, id=id)
    if request.method == 'POST':
        problema.delete()
        messages.success(request, 'El problema ha sido eliminado exitosamente.')
        return redirect('preguntas')
    return render(request, 'confirmar_eliminar_problema.html', {'problema': problema})

@login_required
def ticket_detail(request, id):
    ticket = get_object_or_404(Ticket, id_ticket=id)  # Obtienes el ticket
    historial = HistorialTecnico.objects.filter(ticket=ticket)  # Obtienes el historial del ticket
    user_profile = UserProfile.objects.get(user=request.user)  # Obtienes el perfil del usuario
    estrellas = range(1, 6)  # Rango de estrellas para la calificación (1 a 5)

    return render(request, 'ticket.html', {
        'ticket': ticket, 
        'user_profile': user_profile,
        'estrellas': estrellas,  # Pasamos el rango de estrellas a la plantilla
        'historial': historial
    })


@login_required
def editar_ticket(request, id):
    ticket = get_object_or_404(Ticket, id_ticket=id)

    encargado_anterior = ticket.encargado
    if request.method == 'POST':
        form = TicketFormEdit(request.POST, instance=ticket)
        
        if form.is_valid():
            # Verificar si se cambia el encargado
            nuevo_encargado = form.cleaned_data['encargado']
            if nuevo_encargado != encargado_anterior:
                # Guardar el historial para el cambio de técnico
                HistorialTecnico.objects.create(ticket=ticket, tecnico=nuevo_encargado, motivo="Cambio de técnico")
                ticket.encargado = nuevo_encargado

            # Verificar si el estado es 'R' y la fecha de resolución está vacía
            if form.cleaned_data['estado'] == 'R' and not ticket.fecha_resolucion:
                ticket.fecha_resolucion = timezone.now()
                HistorialTecnico.objects.create(ticket=ticket, tecnico=nuevo_encargado, motivo="Cambio de estado a resuelto")
            
            # Guardar el ticket con los cambios
            form.save()
            messages.success(request, 'El ticket ha sido actualizado exitosamente.')
            return redirect('ticket_detail', id=ticket.id_ticket)
    else:
        form = TicketFormEdit(instance=ticket)

    return render(request, 'editar_ticket.html', {
        'form': form,
        'ticket': ticket,
    })



@login_required
@admin_required
def eliminar_ticket(request, id):
    ticket = get_object_or_404(Ticket, id_ticket=id)
    if request.method == 'POST':
        ticket.delete()
        messages.success(request, 'El ticket ha sido eliminado exitosamente.')
        return redirect('inicio')  # Redirige a la lista de tickets o a otra página
    return render(request, 'confirmar_eliminar.html', {'ticket': ticket})


@login_required
@admin_required
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

    
@login_required
def preguntas(request):
    problemas = ProblemaFrecuente.objects.all()
    user_profile = UserProfile.objects.get(user=request.user)
    return render(request, 'preguntas.html', {
        'problemas': problemas,
        'user_profile': user_profile
    })

def index(request):
    return render(request, 'index.html')

@login_required
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
@admin_required
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

@login_required
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
    prioridad_map = {
        'Baja': 'B',
        'Media': 'M',
        'Alta': 'A'
    }
    
    # Si hay un término de búsqueda, filtra los tickets
    if search_query:
        tickets = tickets.filter(
            Q(usuario__user__username__icontains=search_query) |
            Q(titulo__icontains=search_query) |
            Q(prioridad__icontains=prioridad_map.get(search_query, search_query))|
            Q(categoria__termino__icontains=search_query)|
            Q(estado__icontains=search_query)|
            Q(encargado__user__username__icontains=search_query)|
            Q(fecha_creacion__icontains=search_query)|
            Q(fecha_resolucion__icontains=search_query)|
            Q(comentarios__icontains=search_query)
        )
    
    return render(request, 'inicio.html', {
        'tickets': tickets,
        'user_profile': user_profile,
        'query': search_query
    })




# Vista para la página de tickets
@login_required
@csrf_protect
def tikcet(request):
    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            ticket = form.save(commit=False)
            if not request.user.is_staff:  # Si el usuario no es administrador
                ticket.estado = 'P'
                ticket.prioridad = ''
                ticket.encargado = None  # O establece un valor predeterminado si es necesario
            ticket.categoria = Categoria.objects.get(nombre='General')  # Establece la categoría predeterminada
            ticket.save()
            messages.success(request, 'Tu ticket ha sido creado exitosamente.')
            if ticket.encargado:  # Solo crear historial si hay un técnico asignado
                HistorialTecnico.objects.create(ticket=ticket, tecnico=ticket.encargado)
            
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

@admin_required
@login_required
def editar_equipo(request, id):
    equipo = get_object_or_404(Equipo, id=id)
    if request.method == 'POST':
        form = EquipoForm(request.POST, instance=equipo)
        if form.is_valid():
            form.save()
            messages.success(request, 'El equipo ha sido actualizado exitosamente.')
            return redirect('listar_equipos')
    else:
        form = EquipoForm(instance=equipo)
    return render(request, 'editar_equipo.html', {'form': form})

@admin_required
@login_required
def eliminar_equipo(request, id):
    equipo = get_object_or_404(Equipo, id=id)
    if request.method == 'POST':
        equipo.delete()
        messages.success(request, 'El equipo ha sido eliminado exitosamente.')
        return redirect('listar_equipos')
    return render(request, 'eliminar_equipo.html', {'equipo': equipo})

@admin_required
@login_required
def listar_equipos(request):
    equipos = Equipo.objects.all()
    return render(request, 'listar_equipos.html', {'equipos': equipos})

# Vista para cerrar sesión
@login_required
def logout(request):
    django_logout(request)
    return redirect('login')

# Vista para registrar un usuario
@login_required
def generar_enlace_registro(request, rol_nombre):
    rol = get_object_or_404(Rol, nombre=rol_nombre)
    token = get_random_string(32)
    invitacion = Invitacion.objects.create(rol=rol, token=token)
    enlace_registro = request.build_absolute_uri(f'/registro/{token}/')
    return render(request, 'enlace_registro.html', {'enlace_registro': enlace_registro})


def registro(request, token):
    invitacion = get_object_or_404(Invitacion, token=token, usado=False)

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()  # Guarda el usuario antes de crear el perfil
            # Crear el perfil del usuario con el rol de la invitación
            UserProfile.objects.create(
                user=user,
                rol=invitacion.rol,
                nombre=user.first_name,
                apellidos=user.last_name
            )
            # Marcar la invitación como usada
            invitacion.usado = True
            invitacion.save()
            messages.success(request, 'Registro exitoso.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()

    return render(request, 'registro.html', {'form': form, 'rol': invitacion.rol})