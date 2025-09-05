from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse
from django.forms import ModelForm, DateInput
from .models import Aluno, Curso, CustomUser, Disciplina, PeriodoLetivo, Turma
from .widgets import CustomRelatedFieldWidgetWrapper


class CustomUserForm(UserCreationForm):
    nome = forms.CharField(
        label='Nome',
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Nome'}),
    )
    email = forms.EmailField(
        label='Email',
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Email'}),
    )
    contato = forms.CharField(
        label='Contato',
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Contato'}),
    )
    password1 = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={'placeholder': 'Senha'}),
        strip=False,
    )
    password2 = forms.CharField(
        label='Confirme a senha',
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirmar Senha'}),
        strip=False,
    )

    class Meta:
        model = CustomUser
        fields = ['nome', 'email', 'contato', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.nome = self.cleaned_data['nome']
        user.email = self.cleaned_data['email']
        user.contato = self.cleaned_data['contato']
        user.username = user.email
        if commit:
            user.save()
        return user


class AlunoForm(forms.ModelForm):
    status = forms.ChoiceField(
        label='Status',
        choices=Aluno.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial=1,
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            if not isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-control'})

        rel = Aluno._meta.get_field('curso_interesse').remote_field
        add_url = (
            reverse('cadastrar_curso')
        )
        self.fields[
            'curso_interesse'
        ].widget = CustomRelatedFieldWidgetWrapper(
            self.fields['curso_interesse'].widget, rel, add_url=add_url
        )
        self.fields['curso_interesse'].required = False


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


class DisciplinaForm(forms.ModelForm):
    class Meta:
        model = Disciplina
        fields = [
            'nome',
            'area_conhecimento',
            'curriculo',
            'status',
        ]


class CursoForm(forms.ModelForm):
    class Meta:
        model = Curso
        fields = [
            'nome',
        ]


class TurmaForm(ModelForm):
    class Meta:
        model = Turma
        fields = [
            'nome',
            'capacidade',
            'data_inicio',
            'data_fim',
            'status',
            'periodo_letivo',
            'curso',
        ]
        widgets = {
            'data_inicio': DateInput(attrs={'type': 'date'}),
            'data_fim': DateInput(attrs={'type': 'date'}),
        }