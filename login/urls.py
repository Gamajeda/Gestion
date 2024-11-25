from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('graficas/', views.graficas, name='graficas'),
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),  # Aquí sigue siendo views.login
    path('inicio/', views.inicio, name='inicio'),
    path('perfil/', views.perfil, name='perfil'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
    path('menu/', views.menu, name='menu'),
    path('logout/', views.logout, name='logout'),
    path('tikcet/', views.tikcet, name='tikcet'),
    path('register/', views.register, name='register'),
    path('categoria/', views.categoria, name='categoria'), # Ruta para editar
    path('detalle_ticket/<int:id>/', views.ticket_detail, name='ticket_detail'),
    path('ticket/editar/<int:id>/', views.editar_ticket, name='editar_ticket'),
    path('ticket/calificar/<int:id>/', views.calificar_trabajo, name='calificar_trabajo'),
    path('ticket/eliminar/<int:id>/', views.eliminar_ticket, name='eliminar_ticket'),
    path('todo/', views.todo, name='todo'),
    path('all/', views.all, name='all'),
    path('crear_equipo/', views.crear_equipo, name='crear_equipo'),
    path('preguntas/', views.preguntas, name='preguntas'),
    path('preguntas/editar/<int:id>/', views.editar_problema, name='editar_problema'),
    path('preguntas/eliminar/<int:id>/', views.eliminar_problema, name='eliminar_problema'),
    path('preguntas/detalle/<int:id>/', views.detalle_problema, name='detalle_problema'),
    path('agregar_problema/', views.agregar_problema, name='agregar_problema'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)