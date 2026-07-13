"""
Configuração do aplicativo core.

Registra o nome do app para que o Django o reconheça.
"""
from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Classe de configuração do app core."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Medições de Chuva'
