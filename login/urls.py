from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),  # Aquí sigue siendo views.login
    path('inicio/', views.inicio, name='inicio'),
    path('logout/', views.logout, name='logout'),
    path('tikcet/', views.tikcet, name='tikcet'),
    path('register/', views.register, name='register'),
    path('categoria/', views.categoria, name='categoria'),
    path('editar_ticket/<int:ticket_id>/', views.edit_ticket, name='edit_ticket'),  # Ruta para editar
    path('eliminar_ticket/<int:ticket_id>/', views.delete_ticket, name='delete_ticket'),  # Ruta para eliminar
]
