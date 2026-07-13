"""
Views do app core (baseadas em funções).

Contém a lógica de negócio para gerenciar registros de chuva.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from .models import RegistroChuva, UserProfile
from .forms import RegistroChuvaForm, SomarPeriodoForm, SignupForm, PerfilForm


def get_profile(user):
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile


@login_required
def home(request):
    """
    View principal (home) que exibe as três seções:

    1. Novo registro: formulário para adicionar/atualizar medição.
    2. Somar entre datas: formulário para calcular total em um período.
    3. Últimos registros: tabela com os 10 registros mais recentes.

    Regras de negócio:
    - Se o usuário já tem um registro para a data informada, ele é
      atualizado (sobrescrito) em vez de criar um duplicado.
    - A soma considera apenas registros do usuário logado.
    """
    usuario = request.user

    # --- Processa formulário de novo registro (POST) ---
    if request.method == 'POST' and 'salvar_chuva' in request.POST:
        form = RegistroChuvaForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data['data']
            milimetros = form.cleaned_data['milimetros']
            observacao = form.cleaned_data['observacao']

            # Verifica se já existe um registro para esta data
            registro, criado = RegistroChuva.objects.update_or_create(
                usuario=usuario,
                data=data,
                defaults={
                    'milimetros': milimetros,
                    'observacao': observacao,
                },
            )

            if criado:
                messages.success(
                    request,
                    f'Registro de {milimetros} mm em {data} criado com sucesso!',
                )
            else:
                messages.success(
                    request,
                    f'Registro de {data} atualizado para {milimetros} mm!',
                )

            return redirect('core:home')
    else:
        form = RegistroChuvaForm()

    # --- Processa formulário de soma entre datas (GET ou POST) ---
    total_periodo = None
    registros_periodo = None
    form_soma = SomarPeriodoForm(request.GET or None)

    if form_soma.is_valid():
        inicio = form_soma.cleaned_data['inicio']
        fim = form_soma.cleaned_data['fim']

        registros_periodo = RegistroChuva.objects.filter(
            usuario=usuario,
            data__gte=inicio,
            data__lte=fim,
        ).order_by('data')

        total_periodo = registros_periodo.aggregate(total=Sum('milimetros'))['total']

    # --- Busca os 10 registros mais recentes do usuário ---
    ultimos_registros = RegistroChuva.objects.filter(
        usuario=usuario,
    ).order_by('-data', '-criado_em')[:10]

    profile = get_profile(usuario)
    context = {
        'form': form,
        'form_soma': form_soma,
        'total_periodo': total_periodo,
        'registros_periodo': registros_periodo,
        'ultimos_registros': ultimos_registros,
        'profile': profile,
    }

    return render(request, 'core/home.html', context)


@login_required
def excluir_registro(request, registro_id):
    """
    View para excluir um registro de chuva.

    Regras de negócio:
    - Apenas o dono do registro pode excluí-lo.
    - Usa método POST para evitar exclusão acidental via GET.
    - Redireciona de volta para a home com mensagem de feedback.
    """
    if request.method == 'POST':
        # Busca o registro garantindo que pertence ao usuário logado
        registro = get_object_or_404(
            RegistroChuva,
            id=registro_id,
            usuario=request.user,
        )
        data_str = str(registro.data)
        registro.delete()
        messages.success(
            request,
            f'Registro de {data_str} excluído com sucesso!',
        )
    else:
        messages.error(request, 'Método não permitido para exclusão.')

    return redirect('core:home')


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Conta criada com sucesso! Faça login para continuar.')
            return redirect('login')
    else:
        form = SignupForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def perfil(request):
    profile = get_profile(request.user)
    if request.method == 'POST':
        form = PerfilForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('core:perfil')
    else:
        form = PerfilForm(instance=profile)
    return render(request, 'core/perfil.html', {'form': form, 'profile': profile})
