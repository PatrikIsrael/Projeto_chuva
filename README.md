# 🌧️ Sistema de Controle de Chuva

Aplicação web com Django 4.x para gerenciar medições caseiras de chuva.

## Funcionalidades

- **Autenticação**: login/logout com `django.contrib.auth`
- **Novo registro**: formulário com data, mm e observação; se já existir registro na mesma data, o valor é atualizado (sobrescrito)
- **Somar entre datas**: calcula o total de mm em um período informado
- **Últimos registros**: tabela com os 10 registros mais recentes e botão para excluir cada um

## Estrutura de diretórios

```
projeto_chuva/
├── manage.py               # Gerenciador do Django
├── requirements.txt        # Dependências do projeto
├── db.sqlite3              # Banco de dados SQLite
├── static/                 # Arquivos estáticos globais (opcional)
├── projeto_chuva/          # Configurações do projeto
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── core/                   # App principal
    ├── __init__.py
    ├── admin.py            # Configuração do admin
    ├── apps.py             # Configuração do app
    ├── models.py           # Modelo RegistroChuva
    ├── forms.py            # Formulários
    ├── views.py            # Views (funções)
    ├── urls.py             # URLs do app
    ├── migrations/         # Migrações do banco
    ├── templates/
    │   ├── base.html              # Template base
    │   ├── registration/login.html # Tela de login
    │   └── core/home.html         # Página principal
    └── static/
        └── css/style.css   # CSS personalizado
```

## Como executar

### 1. Pré-requisitos

- Python 3.10 ou superior
- pip (gerenciador de pacotes do Python)

### 2. Clonar ou copiar os arquivos

```bash
cd projeto_chuva
```

### 3. Criar e ativar um ambiente virtual (recomendado)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 5. Executar as migrações

```bash
python manage.py migrate
```

### 6. Criar um superusuário (admin)

```bash
python manage.py createsuperuser
```

Siga as instruções para definir usuário, e-mail e senha.

### 7. Iniciar o servidor

```bash
python manage.py runserver
```

### 8. Acessar

- **Página principal**: http://127.0.0.1:8000/
- **Admin**: http://127.0.0.1:8000/admin/

## Como usar

1. Faça login com o superusuário criado (ou cadastre novos usuários pelo admin)
2. Na página principal, preencha **Data**, **Chuva em mm** e (opcional) **Observação** e clique em "Salvar chuva"
3. Para calcular o total em um período, preencha **Início** e **Fim** e clique em "Calcular"
4. Para excluir um registro, clique em "Excluir" na tabela de últimos registros

## Detalhes técnicos

- **Django 4.2.x** com SQLite
- Views baseadas em funções com `@login_required`
- `unique_together = ('usuario', 'data')` garante um registro por data por usuário
- `update_or_create` para atualizar registro existente na mesma data
- Validação: rejeita mm negativo e data futura
- Mensagens flash para feedback ao usuário
- CSS responsivo sem frameworks externos
