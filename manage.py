#!/usr/bin/env python
"""Utilitário de linha de comando para tarefas administrativas do Django."""
import os
import sys


def main():
    """Executa as tarefas administrativas."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projeto_chuva.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Não foi possível importar o Django. Você tem certeza que ele "
            "está instalado e disponível na sua variável PYTHONPATH? "
            "Você esqueceu de ativar um ambiente virtual?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
