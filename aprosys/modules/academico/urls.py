from django.contrib.auth.views import LogoutView
from django.urls import include, path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
    path('', RedirectView.as_view(url='accounts/login/', permanent=False)),
    path(
        'user_registration/',
        views.user_registration,
        name='user_registration',
    ),
    path('accounts/logout/', LogoutView.as_view(), name='logout'),
    path('home/', views.home, name='home'),
    # --------- Alunos ----------
    path(
        'academico/alunos/pesquisar/',
        views.pesquisar_aluno,
        name='pesquisar_aluno',
    ),
    path('academico/alunos/cadastrar/', views.aluno_form_view, name='cadastrar_aluno'),
    path(
        'academico/alunos/editar/<int:aluno_id>/',
        views.aluno_form_view,
        name='editar_aluno',
    ),
    path(
        'academico/alunos/detalhes/<int:aluno_id>/',
        views.aluno_form_view,
        name='detalhes_aluno',
    ),
    # Anderson

    # --------- Disciplina ----------
    path(
        'academico/disciplinas/cadastrar/',
        views.cadastrar_disciplina,
        name='cadastrar_disciplina',
    ),
    path(
        'academico/disciplinas/pesquisar/',
        views.pesquisar_disciplina,
        name='pesquisar_disciplina',
    ),
    # --------- Período Letivo ----------
    path(
        'academico/periodos/cadastrar/',
        views.cadastrar_periodo,
        name='cadastrar_periodo',
    ),
    path(
        'academico/periodos/pesquisar/',
        views.pesquisar_periodo,
        name='pesquisar_periodo',
    ),
    # --------- Turmas ----------
    path(
        'academico/turmas/cadastrar/',
        views.cadastrar_turma,
        name='cadastrar_turma',
    ),
    path(
        'academico/turmas/pesquisar/',
        views.pesquisar_turma,
        name='pesquisar_turma',
    ),
    # --------- Voluntários ----------
    path(
        'academico/voluntarios/cadastrar/',
        views.cadastrar_voluntario,
        name='cadastrar_voluntario',
    ),
    path(
        'academico/voluntarios/pesquisar/',
        views.pesquisar_voluntario,
        name='pesquisar_voluntario',
    ),
    # --------- Cursos ----------
    path(
        'academico/cursos/cadastrar/',
        views.cadastrar_curso,
        name='cadastrar_curso',
    ),
    path(
        'academico/cursos/pesquisar/',
        views.pesquisar_curso,
        name='pesquisar_curso',
    ),
]
