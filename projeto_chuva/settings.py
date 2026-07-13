"""
Configurações principais do projeto Django "projeto_chuva".

Gera as configurações para o ambiente de desenvolvimento.
"""
import os
from pathlib import Path

# Caminho base do projeto (diretório que contém manage.py)
BASE_DIR = Path(__file__).resolve().parent.parent

# Chave secreta (em produção, troque por uma chave real e não versionada)
SECRET_KEY = 'django-insecure-chave-mockada-para-desenvolvimento-mude-em-producao'

# Modo de depuração (desligar em produção)
DEBUG = True

# Hosts permitidos (em produção, especifique os domínios reais)
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '192.168.0.147']


# ----------------------------------------------------------------------
# Aplicações instaladas
# ----------------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',          # Interface administrativa
    'django.contrib.auth',           # Sistema de autenticação
    'django.contrib.contenttypes',   # Framework de tipos de conteúdo
    'django.contrib.sessions',       # Gerenciamento de sessões
    'django.contrib.messages',       # Sistema de mensagens flash
    'django.contrib.staticfiles',    # Gerenciamento de arquivos estáticos

    # Nosso app principal que contém as funcionalidades de medição de chuva
    'core.apps.CoreConfig',
]

# ----------------------------------------------------------------------
# Middleware (processamento de requisições/respostas)
# ----------------------------------------------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Arquivo de configuração de URLs raiz
ROOT_URLCONF = 'projeto_chuva.urls'

# ----------------------------------------------------------------------
# Configuração de templates
# ----------------------------------------------------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # O Django procura templates dentro de cada app (APP_DIRS=True)
        'DIRS': [],  # Diretórios adicionais de templates (opcional)
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Aplicação WSGI para servidores de produção
WSGI_APPLICATION = 'projeto_chuva.wsgi.application'


# ----------------------------------------------------------------------
# Banco de dados (SQLite – padrão para desenvolvimento)
# ----------------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# ----------------------------------------------------------------------
# Validação de senhas (regras de segurança para autenticação)
# ----------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ----------------------------------------------------------------------
# Internacionalização
# ----------------------------------------------------------------------
LANGUAGE_CODE = 'pt-br'       # Português do Brasil
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True


# ----------------------------------------------------------------------
# Arquivos estáticos (CSS, JS, imagens)
# ----------------------------------------------------------------------
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    # Diretório global de estáticos (fora dos apps)
    BASE_DIR / 'static',
]

# ----------------------------------------------------------------------
# Configurações de autenticação
# ----------------------------------------------------------------------
# URL para onde redirecionar quando o usuário não está logado
LOGIN_URL = '/login/'
# URL para onde redirecionar após login bem-sucedido
LOGIN_REDIRECT_URL = '/'
# URL para onde redirecionar após logout
LOGOUT_REDIRECT_URL = '/login/'

# ----------------------------------------------------------------------
# Configuração de campo de chave primária padrão
# ----------------------------------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
