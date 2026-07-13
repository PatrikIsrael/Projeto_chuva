"""
Configuração WSGI para o projeto projeto_chuva.

Expõe a aplicação WSGI como uma variável de nível de módulo chamada ``application``.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projeto_chuva.settings')

application = get_wsgi_application()
