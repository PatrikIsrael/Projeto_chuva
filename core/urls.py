"""
Mapeamento de URLs do app core.

Define as rotas para a página principal e para a exclusão de registros.
"""
from django.urls import path
from . import views

# Nome do app para referência nos templates (ex: 'core:home')
app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('perfil/', views.perfil, name='perfil'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('excluir/<int:registro_id>/', views.excluir_registro, name='excluir_registro'),
]
