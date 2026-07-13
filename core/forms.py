"""
Formulários Django para o app core.

Define os formulários usados na página principal:
- RegistroChuvaForm: para criar/atualizar medições
- SomarPeriodoForm: para selecionar o intervalo de datas da soma
- SignupForm: cadastro completo com telefone
- PerfilForm: configurações de tema e paleta
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import RegistroChuva, UserProfile


class RegistroChuvaForm(forms.ModelForm):
    """
    Formulário para criar ou atualizar um registro de chuva.

    Usa ModelForm para gerar automaticamente os campos com base no modelo.
    """

    class Meta:
        """Configura o formulário a partir do modelo."""

        model = RegistroChuva
        # Campos que aparecerão no formulário (excluindo usuario e timestamps)
        fields = ['data', 'milimetros', 'observacao']

        # Personaliza os widgets (aparência HTML) dos campos
        widgets = {
            'data': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'},
                format='%Y-%m-%d',
            ),
            'milimetros': forms.NumberInput(
                attrs={
                    'step': '0.1',
                    'class': 'form-control',
                    'placeholder': 'Ex: 12.5',
                },
            ),
            'observacao': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Opcional: observações sobre a medição',
                },
            ),
        }

        # Rótulos dos campos em português
        labels = {
            'data': 'Data',
            'milimetros': 'Chuva em mm',
            'observacao': 'Observação',
        }

    def clean_milimetros(self):
        """
        Validação personalizada para o campo milimetros.

        Regra de negócio: o valor não pode ser negativo e não pode
        ultrapassar um limite razoável (ex: 999.9 mm).
        """
        valor = self.cleaned_data.get('milimetros')
        if valor is not None:
            if valor < 0:
                raise forms.ValidationError('O valor de chuva não pode ser negativo.')
            if valor > 999.9:
                raise forms.ValidationError('O valor de chuva parece muito alto (máx: 999.9 mm).')
        return valor

    def clean_data(self):
        """
        Validação personalizada para o campo data.

        Regra de negócio: a data não pode ser futura (não podemos medir
        chuva que ainda não aconteceu).
        """
        from datetime import date
        data = self.cleaned_data.get('data')
        if data and data > date.today():
            raise forms.ValidationError('A data não pode ser futura.')
        return data


class SomarPeriodoForm(forms.Form):
    """
    Formulário simples para capturar as datas de início e fim
    para calcular o total de chuva em um período.
    """
    inicio = forms.DateField(
        label='Início',
        widget=forms.DateInput(
            attrs={'type': 'date', 'class': 'form-control'},
            format='%Y-%m-%d',
        ),
    )
    fim = forms.DateField(
        label='Fim',
        widget=forms.DateInput(
            attrs={'type': 'date', 'class': 'form-control'},
            format='%Y-%m-%d',
        ),
    )

    def clean(self):
        """
        Validação geral: verifica se a data de início é anterior à data de fim.
        """
        dados = super().clean()
        inicio = dados.get('inicio')
        fim = dados.get('fim')
        if inicio and fim and inicio > fim:
            raise forms.ValidationError(
                'A data de início deve ser anterior ou igual à data de fim.'
            )
        return dados


class SignupForm(UserCreationForm):
    telefone = forms.CharField(
        max_length=20, required=False,
        label='Telefone',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '(11) 99999-8888',
        }),
    )

    class Meta:
        model = User
        fields = ['username', 'telefone', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            attrs = field.widget.attrs
            if 'class' not in attrs:
                attrs['class'] = 'form-control'
            if 'placeholder' not in attrs:
                attrs['placeholder'] = field.label or ''

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            UserProfile.objects.create(
                user=user,
                telefone=self.cleaned_data.get('telefone', ''),
            )
        return user


class PerfilForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['telefone', 'tema', 'paleta_cores']
        widgets = {
            'telefone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(11) 99999-8888',
            }),
            'tema': forms.Select(attrs={'class': 'form-control'}),
            'paleta_cores': forms.Select(attrs={'class': 'form-control'}),
        }
