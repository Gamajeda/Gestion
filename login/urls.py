from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),  # Aquí sigue siendo views.login
    path('inicio/', views.inicio, name='inicio'),
    path('logout/', views.logout, name='logout'),
    path('tikcet/', views.tikcet, name='tikcet'),
    path('register/', views.register, name='register'),
]
