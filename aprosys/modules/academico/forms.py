# cadastros/forms.py
from django import forms

from .models import Aluno, PeriodoLetivo


class AlunoForm(forms.ModelForm):
    status = forms.ChoiceField(
        label='Status',
        choices=Aluno.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial=1,  # * 1 = “Ativo” por default
    )

    class Meta:
        model = Aluno
        fields = [
            'nome',
            'email',
            'contato',
            'nascimento',
            'nacionalidade',
            'naturalidade',
            'estado_civil',
            'nome_pai',
            'escolaridade_pai',
            'nome_mae',
            'escolaridade_mae',
            'renda_familiar',
            'rua',
            'numero',
            'complemento',
            'bairro',
            'cidade',
            'estado',
            'cep',
            'status',
            'curso_interesse',
            'periodo_interesse',
        ]


class PeriodoLetivoForm(forms.ModelForm):
    class Meta:
        model = PeriodoLetivo
        fields = [
            'nome',
            'data_inicio',
            'data_fim',
            'ano',
            'semestre',
            'status',
        ]
        widgets = {
            'nome': forms.HiddenInput(),
        }
