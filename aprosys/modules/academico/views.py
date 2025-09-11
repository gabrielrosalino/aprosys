from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect, render, get_object_or_404

from .forms import (
    AlunoForm,
    CursoForm,
    CustomUserForm,
    DisciplinaForm,
    PeriodoLetivoForm,
    TurmaForm,
    VoluntarioForm,
)
from .models import (
    Aluno,
    Curso,
    Disciplina,
    PeriodoLetivo,
    Turma,
    TurmaAluno,
    TurmaDisciplinaProfessor,
    Voluntario,
)


def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            if not request.user.is_authenticated:
                return redirect('login')
            if not hasattr(request.user, 'voluntario'):
                return HttpResponseForbidden()
            if request.user.voluntario.tipo_voluntario not in allowed_roles:
                return HttpResponseForbidden()
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator


def user_registration(request):
    if request.method == 'POST':
        form = CustomUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cadastro realizado com sucesso!')
            return redirect('login')
    else:
        form = CustomUserForm()
    return render(
        request, 'registration/user_registration.html', {'form': form}
    )


@login_required
def home(request):
    return render(request, 'academico/home.html')


# --------- Alunos ----------
@login_required
def pesquisar_aluno(request):
    query = request.GET.get('q', '')
    order = request.GET.get('order', 'nome')
    dir = request.GET.get('dir', 'asc')

    voluntario = getattr(request.user, 'voluntario', None)

    alunos = Aluno.objects.all()

    if voluntario and voluntario.tipo_voluntario == 'PROFESSOR':
        turmas_ids = (
            TurmaDisciplinaProfessor.objects.filter(
                voluntario=voluntario, status=1, turma_disciplina__status=1
            )
            .values_list('turma_disciplina__turma_id', flat=True)
            .distinct()
        )

        alunos_ids = (
            TurmaAluno.objects.filter(turma_id__in=turmas_ids, status=1)
            .values_list('aluno_id', flat=True)
            .distinct()
        )

        alunos = Aluno.objects.filter(id__in=alunos_ids)

    if query:
        alunos = alunos.filter(nome__icontains=query)

    if dir == 'desc':
        order = f'-{order}'
    alunos = alunos.order_by(order)

    context = {
        'alunos': alunos,
        'q': query,
        'order': request.GET.get('order', 'nome'),
        'dir': request.GET.get('dir', 'asc'),
    }

    return render(request, 'academico/alunos/pesquisar_aluno.html', context)


@role_required(['COORDENADOR'])
@login_required
def matricular_aluno(request):
    if request.method == 'POST':
        form = AlunoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('pesquisar_aluno')
    else:
        form = AlunoForm()

    return render(
        request,
        'academico/alunos/matricular_aluno.html',
        {'form': form, 'active_menu': 'alunos'},
    )

# Anderson
@role_required(['COORDENADOR'])
@login_required
def editar_aluno(request, aluno_id):
    aluno = get_object_or_404(Aluno, pk=aluno_id)

    if request.method == 'POST':
        form = AlunoForm(request.POST, instance=aluno)
        if form.is_valid():
            form.save() 
            messages.success(request, 'Aluno atualizado com sucesso!')
            return redirect('pesquisar_aluno')  
    else:
        form = AlunoForm(instance=aluno)

    return render(
        request,
        'academico/alunos/editar_aluno.html',
        {'form': form, 'active_menu': 'alunos'},
    )
# Anderson

# --------- Disciplina ----------
@role_required(['COORDENADOR'])
@login_required
def cadastrar_disciplina(request):
    if request.method == 'POST':
        form = DisciplinaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cadastrar_disciplina')
    else:
        form = DisciplinaForm()
    return render(
        request,
        'academico/disciplinas/cadastrar_disciplina.html',
        {
            'form': form,
            'active_menu': 'disciplina',
        },
    )


@login_required
def pesquisar_disciplina(request):
    q = request.GET.get('q', '').strip()
    voluntario = getattr(request.user, 'voluntario', None)

    disciplinas = Disciplina.objects.all()

    if voluntario and voluntario.tipo_voluntario == 'PROFESSOR':
        # Disciplinas vinculadas ao professor via TurmaDisciplinaProfessor
        disciplina_ids = (
            TurmaDisciplinaProfessor.objects.filter(
                voluntario=voluntario, status=1, turma_disciplina__status=1
            )
            .values_list('turma_disciplina__disciplina_id', flat=True)
            .distinct()
        )
        disciplinas = disciplinas.filter(id__in=disciplina_ids)

    if q:
        disciplinas = disciplinas.filter(
            Q(nome__icontains=q) | Q(area_conhecimento__icontains=q)
        )

    allowed_fields = {
        'nome': 'nome',
        'area_conhecimento': 'area_conhecimento',
        'status': 'status',
    }
    order = request.GET.get('order', 'nome')
    direction = request.GET.get('dir', 'asc')

    if order not in allowed_fields:
        order = 'nome'

    prefix = '' if direction == 'asc' else '-'
    disciplinas = disciplinas.order_by(f'{prefix}{allowed_fields[order]}')

    return render(
        request,
        'academico/disciplinas/pesquisar_disciplina.html',
        {
            'disciplinas': disciplinas,
            'q': q,
            'order': order,
            'dir': direction,
            'active_menu': 'disciplinas',
        },
    )


# --------- Período Letivo ----------
@role_required(['COORDENADOR'])
@login_required
def cadastrar_periodo(request):
    if request.method == 'POST':
        form = PeriodoLetivoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cadastrar_periodo')
    else:
        form = PeriodoLetivoForm()
    return render(
        request, 'academico/periodos/cadastrar_periodo.html', {'form': form}
    )


# --------- Cursos ----------
@role_required(['COORDENADOR'])
@login_required
def cadastrar_curso(request):
    field_name = request.GET.get('field_name') or request.POST.get(
        'field_name'
    )

    if request.method == 'POST':
        form = CursoForm(request.POST)
        if form.is_valid():
            curso = form.save()

            if field_name:
                return HttpResponse(f"""
                    <script>
                        if (window.opener) {{
                            window.opener.postMessage({{
                                type: 'add_related',
                                name: '{field_name}',
                                value: '{curso.id_curso}',
                                text: '{curso.nome.replace("'", "\\'")}'
                            }}, '*');
                        }}
                        setTimeout(function() {{
                            window.close();
                        }}, 100);
                    </script>
                    <div style='padding: 20px; text-align: center;'>
                        <h3>Curso cadastrado com sucesso!</h3>
                        <p>Esta aba será fechada automaticamente.</p>
                    </div>
                """)
            else:
                return redirect('pesquisar_curso')
        else:
            return render(
                request,
                'academico/cursos/cadastrar_curso.html',
                {'form': form, 'field_name': field_name},
            )

    else:
        form = CursoForm()
        print(f'DEBUG - GET request, field_name: {field_name}')

    return render(
        request,
        'academico/cursos/cadastrar_curso.html',
        {'form': form, 'field_name': field_name},
    )


@login_required
def pesquisar_curso(request):
    q = request.GET.get('q', '').strip()
    cursos = Curso.objects.all()

    if q:
        cursos = cursos.filter(Q(nome__icontains=q))

    allowed_fields = {
        'nome': 'nome',
    }
    order = request.GET.get('order', 'nome')
    direction = request.GET.get('dir', 'asc')

    if order not in allowed_fields:
        order = 'nome'

    prefix = '' if direction == 'asc' else '-'
    cursos = cursos.order_by(f'{prefix}{allowed_fields[order]}')

    return render(
        request,
        'academico/cursos/pesquisar_curso.html',
        {
            'cursos': cursos,
            'q': q,
            'order': order,
            'dir': direction,
            'active_menu': 'cursos',
        },
    )


@role_required(['COORDENADOR'])
@login_required
def pesquisar_periodo(request):
    q = request.GET.get('q', '').strip()
    periodos = PeriodoLetivo.objects.all()

    if q:
        # Permite buscar por nome, ano ou semestre
        periodos = periodos.filter(
            Q(nome__icontains=q)
            | Q(ano__icontains=q)
            | Q(semestre__icontains=q)
        )

    allowed_fields = {
        'nome': 'nome',
        'ano': 'ano',
        'semestre': 'semestre',
        'data_inicio': 'data_inicio',
        'data_fim': 'data_fim',
        'status': 'status',
    }
    order = request.GET.get('order', 'nome')
    direction = request.GET.get('dir', 'asc')

    if order not in allowed_fields:
        order = 'nome'

    prefix = '' if direction == 'asc' else '-'
    periodos = periodos.order_by(f'{prefix}{allowed_fields[order]}')

    return render(
        request,
        'academico/periodos/pesquisar_periodo.html',
        {
            'periodos': periodos,
            'q': q,
            'order': order,
            'dir': direction,
            'active_menu': 'periodo',
        },
    )


# --------- Turmas ----------
@role_required(['COORDENADOR'])
@login_required
def cadastrar_turma(request):
    if request.method == 'POST':
        form = TurmaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Turma cadastrada com sucesso!')
            return redirect('pesquisar_turma')
    else:
        form = TurmaForm()

    return render(
        request,
        'academico/turmas/cadastrar_turma.html',
        {'form': form, 'active_menu': 'turmas'},
    )



@login_required
def pesquisar_turma(request):
    q = request.GET.get('q', '').strip()
    voluntario = getattr(request.user, 'voluntario', None)

    turmas = Turma.objects.all()

    if voluntario and voluntario.tipo_voluntario == 'PROFESSOR':
        # Filtra turmas onde o professor leciona via TurmaDisciplinaProfessor
        turmas_ids = (
            TurmaDisciplinaProfessor.objects.filter(
                voluntario=voluntario, status=1, turma_disciplina__status=1
            )
            .values_list('turma_disciplina__turma_id', flat=True)
            .distinct()
        )
        turmas = turmas.filter(id_turma__in=turmas_ids)

    if q:
        turmas = turmas.filter(
            Q(nome__icontains=q) | Q(periodo_letivo__nome__icontains=q)
        )

    allowed_fields = {
        'nome': 'nome',
        'capacidade': 'capacidade',
        'data_inicio': 'data_inicio',
        'data_fim': 'data_fim',
        'status': 'status',
        'periodo_letivo': 'periodo_letivo__nome',
    }
    order = request.GET.get('order', 'nome')
    direction = request.GET.get('dir', 'asc')

    if order not in allowed_fields:
        order = 'nome'

    prefix = '' if direction == 'asc' else '-'
    turmas = turmas.order_by(f'{prefix}{allowed_fields[order]}')

    return render(
        request,
        'academico/turmas/pesquisar_turma.html',
        {
            'turmas': turmas,
            'q': q,
            'order': order,
            'dir': direction,
            'active_menu': 'turmas',
        },
    )


# --------- Voluntários ----------
@role_required(['COORDENADOR'])
@login_required
def cadastrar_voluntario(request):
    if request.method == 'POST':
        form = VoluntarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Voluntário cadastrado com sucesso!')
            return redirect('pesquisar_voluntario')
    else:
        form = VoluntarioForm()

    return render(
        request,
        'academico/voluntarios/cadastrar_voluntario.html',
        {'form': form, 'active_menu': 'voluntarios'},
    )


@login_required
def pesquisar_voluntario(request):
    q = request.GET.get('q', '').strip()
    order = request.GET.get('order', 'nome')
    direction = request.GET.get('dir', 'asc')

    voluntarios = Voluntario.objects.all()

    if q:
        voluntarios = voluntarios.filter(
            Q(nome__icontains=q) | Q(email__icontains=q)
        )

    allowed_sort_fields = {
        'nome': 'nome',
        'email': 'email',
        'tipo_voluntario': 'tipo_voluntario',
        'status': 'status_processo_voluntario',
    }
    sort_field = allowed_sort_fields.get(order, 'nome')

    if direction == 'desc':
        sort_field = f'-{sort_field}'

    voluntarios = voluntarios.order_by(sort_field)

    context = {
        'voluntarios': voluntarios,
        'q': q,
        'order': order,
        'dir': direction,
        'active_menu': 'voluntarios',
    }
    return render(
        request, 'academico/voluntarios/pesquisar_voluntario.html', context
    )
