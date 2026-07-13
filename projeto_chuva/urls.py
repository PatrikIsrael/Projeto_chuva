"""
Mapeamento de URLs raiz do projeto projeto_chuva.

Inclui as URLs de autenticação (login/logout) e as URLs do app core.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Rota para o painel administrativo do Django
    path('admin/', admin.site.urls),

    # Inclui todas as URLs de autenticação: login, logout, etc.
    path('', include('django.contrib.auth.urls')),

    # Inclui as URLs do nosso app core (página principal, exclusão, etc.)
    path('', include('core.urls')),
]
