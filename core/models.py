"""
Modelos de dados do app core.

Define a estrutura do banco de dados para armazenar as medições de chuva.
"""
from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    THEME_CHOICES = [
        ('light', 'Claro'),
        ('dark', 'Escuro'),
    ]
    PALETTE_CHOICES = [
        ('default', 'Padrão (Azul)'),
        ('forest', 'Floresta (Verde)'),
        ('sunset', 'Pôr do Sol (Laranja)'),
        ('ocean', 'Oceano (Turquesa)'),
        ('lavender', 'Lavanda (Roxo)'),
        ('ruby', 'Rubi (Vermelho)'),
    ]
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile'
    )
    telefone = models.CharField(
        max_length=20, blank=True, null=True, verbose_name='Telefone'
    )
    tema = models.CharField(
        max_length=10, choices=THEME_CHOICES, default='light',
        verbose_name='Tema'
    )
    paleta_cores = models.CharField(
        max_length=20, choices=PALETTE_CHOICES, default='default',
        verbose_name='Paleta de Cores'
    )

    class Meta:
        verbose_name = 'Perfil do Usuário'
        verbose_name_plural = 'Perfis dos Usuários'

    def __str__(self):
        return f'Perfil de {self.user.username}'


class RegistroChuva(models.Model):
    """
    Armazena uma medição de chuva feita por um usuário em uma determinada data.

    Regras de negócio:
    - Cada usuário pode ter no máximo UM registro por data.
    - O campo milimetros aceita valores decimais (ex: 12.5 mm).
    - O campo observacao é opcional.
    - As datas criado_em e atualizado_em são preenchidas automaticamente.
    """

    # Relacionamento com o usuário autenticado
    # on_delete=CASCADE: se o usuário for excluído, seus registros também são
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Usuário',
        related_name='registros_chuva',
    )

    # Data da medição (sem hora)
    data = models.DateField(
        verbose_name='Data da medição',
    )

    # Quantidade de chuva em milímetros, com 1 casa decimal
    # Exemplo: 12.5 mm, max_digits=5 permite valores até 999.9
    milimetros = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        verbose_name='Chuva (mm)',
    )

    # Observação opcional sobre a medição
    observacao = models.TextField(
        blank=True,      # Pode ficar vazio no formulário
        null=True,       # Pode ser NULL no banco de dados
        verbose_name='Observação',
    )

    # Timestamps automáticos
    criado_em = models.DateTimeField(
        auto_now_add=True,  # Preenchido automaticamente na criação
        verbose_name='Criado em',
    )
    atualizado_em = models.DateTimeField(
        auto_now=True,       # Atualizado automaticamente a cada salvamento
        verbose_name='Atualizado em',
    )

    class Meta:
        """Metadados do modelo."""

        # Garante que cada usuário tenha apenas um registro por data
        unique_together = ('usuario', 'data')

        # Ordem padrão: registros mais recentes primeiro
        ordering = ['-data', '-criado_em']

        verbose_name = 'Registro de Chuva'
        verbose_name_plural = 'Registros de Chuva'

    def __str__(self):
        """Representação em string do registro."""
        return f'{self.usuario.username} - {self.data}: {self.milimetros} mm'
