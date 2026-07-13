"""
Configuração do admin para o modelo RegistroChuva.

Permite gerenciar os registros de chuva diretamente pelo painel admin do Django.
"""
from django.contrib import admin
from .models import RegistroChuva, UserProfile


@admin.register(RegistroChuva)
class RegistroChuvaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'data', 'milimetros', 'criado_em')
    list_filter = ('usuario', 'data')
    search_fields = ('usuario__username', 'observacao')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'telefone', 'tema', 'paleta_cores')
    list_filter = ('tema', 'paleta_cores')
    search_fields = ('user__username', 'telefone')
