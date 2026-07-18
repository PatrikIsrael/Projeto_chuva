"""
Views do app core (baseadas em funções).

Contém a lógica de negócio para gerenciar registros de chuva.
"""
import json
from datetime import date, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Avg
from django.db.models.functions import TruncMonth
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


@login_required
def dashboard(request):
    usuario = request.user
    registros = RegistroChuva.objects.filter(usuario=usuario).order_by('data')

    # --- Estatísticas globais ---
    total_anual = registros.aggregate(total=Sum('milimetros'))['total'] or 0
    total_registros = registros.count()
    maior_valor = registros.order_by('-milimetros').first()
    menor_valor_com_registro = registros.order_by('milimetros').first()

    # --- Agrupamento por mês (para o gráfico mensal) ---
    meses = (
        registros
        .annotate(mes=TruncMonth('data'))
        .values('mes')
        .annotate(
            total=Sum('milimetros'),
            quantidade=Count('id'),
            media=Avg('milimetros'),
        )
        .order_by('mes')
    )

    meses_labels = []
    meses_totals = []
    meses_medias = []
    meses_qtd = []
    for m in meses:
        meses_labels.append(m['mes'].strftime('%b/%Y'))
        meses_totals.append(float(m['total']))
        meses_medias.append(round(float(m['media']), 1))
        meses_qtd.append(m['quantidade'])

    media_mensal = round(float(total_anual / total_registros), 1) if total_registros else 0

    # --- Comparação de períodos ---
    today = date.today()

    # Lê parâmetros da URL ou usa defaults (mês atual vs mês anterior)
    inicio_a = request.GET.get('inicio_a', '')
    fim_a = request.GET.get('fim_a', '')
    inicio_b = request.GET.get('inicio_b', '')
    fim_b = request.GET.get('fim_b', '')

    if not inicio_a or not fim_a:
        primeiro_dia_mes = today.replace(day=1)
        inicio_a = primeiro_dia_mes.isoformat()
        fim_a = today.isoformat()

    if not inicio_b or not fim_b:
        ultimo_dia_mes_anterior = today.replace(day=1) - timedelta(days=1)
        primeiro_dia_mes_anterior = ultimo_dia_mes_anterior.replace(day=1)
        inicio_b = primeiro_dia_mes_anterior.isoformat()
        fim_b = ultimo_dia_mes_anterior.isoformat()

    def period_stats(inicio, fim):
        qs = registros.filter(data__gte=inicio, data__lte=fim)
        total = qs.aggregate(s=Sum('milimetros'))['s'] or 0
        qtd = qs.count()
        media = round(float(total / qtd), 1) if qtd else 0
        max_reg = qs.order_by('-milimetros').first()
        min_reg = qs.order_by('milimetros').first()
        return {
            'total': round(float(total), 1),
            'qtd': qtd,
            'media': media,
            'max': max_reg,
            'min': min_reg,
            'inicio': inicio,
            'fim': fim,
        }

    stats_a = period_stats(inicio_a, fim_a)
    stats_b = period_stats(inicio_b, fim_b)

    # Dados para o gráfico de comparação (agrupado por dia)
    def period_daily(inicio, fim):
        qs = registros.filter(data__gte=inicio, data__lte=fim).order_by('data')
        dias = {}
        for r in qs:
            dias[r.data.isoformat()] = dias.get(r.data.isoformat(), 0) + float(r.milimetros)
        return dias

    dias_a = period_daily(inicio_a, fim_a)
    dias_b = period_daily(inicio_b, fim_b)

    all_dates = sorted(set(list(dias_a.keys()) + list(dias_b.keys())))
    comp_labels = []
    comp_values_a = []
    comp_values_b = []
    for d in all_dates:
        comp_labels.append(d)
        comp_values_a.append(dias_a.get(d, 0))
        comp_values_b.append(dias_b.get(d, 0))

    profile = get_profile(usuario)
    context = {
        # Globais
        'total_anual': round(float(total_anual), 1),
        'total_registros': total_registros,
        'media_mensal': media_mensal,
        'maior_valor': maior_valor,
        'menor_valor': menor_valor_com_registro,
        'meses_labels': json.dumps(meses_labels),
        'meses_totals': json.dumps(meses_totals),
        'meses_medias': json.dumps(meses_medias),
        'meses_qtd': json.dumps(meses_qtd),
        'meses_data': meses,
        # Comparação
        'stats_a': stats_a,
        'stats_b': stats_b,
        'inicio_a': inicio_a,
        'fim_a': fim_a,
        'inicio_b': inicio_b,
        'fim_b': fim_b,
        'comp_labels_json': json.dumps(comp_labels),
        'comp_labels': comp_labels,
        'comp_values_a': json.dumps(comp_values_a),
        'comp_values_b': json.dumps(comp_values_b),
        'profile': profile,
    }
    return render(request, 'core/dashboard.html', context)
