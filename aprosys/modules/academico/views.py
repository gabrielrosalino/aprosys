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

#region --- UTILITÁRIOS, AUTENTICAÇÃO E NAVEGAÇÃO BASE ---  

# Decorator personalizado para restringir o acesso a views com base no tipo de voluntário
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

# Gerencia a criação de novos usuários no sistema através do CustomUserForm e redireciona para o login após o sucesso
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

# Renderiza a página inicial (Dashboard) do sistema Aprova System após o login
@login_required
def home(request):
    return render(request, 'academico/home.html')
#endregion ---

#region --- ALUNOS - ANDERSON ---
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

@login_required
@role_required(['COORDENADOR'])
def aluno_form_view(request, aluno_id=None):
    """
    View unificada para Matricular, Editar e Ver Detalhes de um Aluno.
    """
    # 1. Determina o modo (matricular, editar, detalhes) a partir do nome da URL
    modo = request.resolver_match.url_name

    # # 2. Verifica as permissões de acesso DENTRO da view
    # if not request.user.is_authenticated:
    #     return redirect('login')

    # # Ações que exigem a role de Coordenador
    # if modo in ['cadastrar_aluno', 'editar_aluno']:
    #     if not request.user.is_superuser:
    #         if not hasattr(request.user, 'voluntario') or request.user.voluntario.tipo_voluntario != 'COORDENADOR':
    #             return HttpResponseForbidden("Você não tem permissão para acessar esta página.")

    # 3. Lógica para buscar o aluno ou criar um novo
    aluno_instance = None
    if aluno_id:
        aluno_instance = get_object_or_404(Aluno, pk=aluno_id)

    # 4. Lógica para salvar o formulário (apenas em modo de edição/matrícula)
    if request.method == 'POST' and modo != 'detalhes_aluno':
        form = AlunoForm(request.POST, instance=aluno_instance)
        if form.is_valid():
            form.save()
            acao = "cadastrado" if modo == 'cadastrar_aluno' else "atualizado"
            messages.success(request, f'Aluno {acao} com sucesso!')
            return redirect('pesquisar_aluno')
    else:
        form = AlunoForm(instance=aluno_instance)

    # 5. Desabilita os campos se estivermos apenas visualizando
    if modo == 'detalhes_aluno':
        for field in form.fields.values():
            field.widget.attrs['disabled'] = True

    # 6. Envia tudo para o template
    context = {
        'form': form,
        'aluno': aluno_instance,
        'modo': modo,
        'active_menu': 'alunos'
    }
    return render(request, 'academico/alunos/aluno_form.html', context)
#endregion ---

#region --- DISCIPLINA - LORENA ---

# View unificada para Cadastrar e Editar Disciplina. Suporta abertura via popup para campos relacionados.
@role_required(['COORDENADOR'])
@login_required
def cadastrar_disciplina(request, disciplina_id=None):
    
    disciplina_instance = None
    
    if disciplina_id:
        disciplina_instance = get_object_or_404(Disciplina, pk=disciplina_id)

    if request.method == 'POST':
        form = DisciplinaForm(request.POST, instance=disciplina_instance)
        if form.is_valid():
            disciplina = form.save()
            acao = "atualizada" if disciplina_id else "criada"
            messages.success(request, f'Disciplina "{disciplina.nome}" {acao} com êxito!')
            return redirect('pesquisar_disciplina')
    else:
        form = DisciplinaForm(instance=disciplina_instance)
    
    return render(
        request,
        'academico/disciplinas/cadastrar_disciplina.html',
        {
            'form': form,
            'disciplina': disciplina_instance, 
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


# Exclui uma disciplina específica do banco de dados e retorna    uma mensagem de confirmação
@role_required(['COORDENADOR'])
@login_required
def excluir_disciplina(request, disciplina_id):
    disciplina = get_object_or_404(Disciplina, pk=disciplina_id)
    nome_disciplina = disciplina.nome
    disciplina.delete()
    
    messages.success(request, f'Disciplina "{nome_disciplina}" excluída com sucesso!')
    return redirect('pesquisar_disciplina')


# Recebe uma lista de IDs via POST e exclui as disciplinas correspondentes.
@role_required(['COORDENADOR'])
@login_required
def excluir_disciplinas_massa(request):

    if request.method == 'POST':
        ids_raw = request.POST.get('disciplina_ids', '')
        if ids_raw:
            ids_list = ids_raw.split(',')
            # O delete() retorna uma tupla, onde o primeiro item é a contagem
            count = Disciplina.objects.filter(pk__in=ids_list).delete()[0]
            messages.success(request, f'{count} disciplinas excluídas com sucesso!')
    return redirect('pesquisar_disciplina')

#endregion ---

#region --- PERÍODO LETIVO --- 
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
#endregion ---

#region --- CURSOS - LORENA ---

# View unificada para Cadastrar e Editar Cursos. Suporta abertura via popup para campos relacionados.
@role_required(['COORDENADOR'])
@login_required
def cadastrar_curso(request, curso_id=None):
    field_name = request.GET.get('field_name') or request.POST.get('field_name')
    
    # Busca a instância para edição ou inicia como None para novo cadastro
    curso_instance = None
    if curso_id:
        curso_instance = get_object_or_404(Curso, pk=curso_id)

    if request.method == 'POST':
        form = CursoForm(request.POST, instance=curso_instance)
        if form.is_valid():
            curso = form.save()
            
            # Lógica para fechamento automático se for aberto via popup
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
                        setTimeout(function() {{ window.close(); }}, 100);
                    </script>
                    <div style='padding: 20px; text-align: center; font-family: sans-serif;'>
                        <h3>Curso salvo com sucesso!</h3>
                        <p>Esta janela será fechada automaticamente.</p>
                    </div>
                """)
            
            acao = "atualizado" if curso_id else "cadastrado"
            messages.success(request, f'Curso "{curso.nome}" {acao} com sucesso!')
            return redirect('pesquisar_curso')
    else:
        form = CursoForm(instance=curso_instance)

    return render(
        request,
        'academico/cursos/cadastrar_curso.html',
        {
            'form': form, 
            'field_name': field_name, 
            'curso': curso_instance,
            'active_menu': 'cursos'
        }
    )


# Lista os cursos com suporte a busca por nome e ordenação.
@login_required
def pesquisar_curso(request):

    q = request.GET.get('q', '').strip()
    cursos = Curso.objects.all()

    if q:
        cursos = cursos.filter(Q(nome__icontains=q))

    order = request.GET.get('order', 'nome')
    direction = request.GET.get('dir', 'asc')
    prefix = '' if direction == 'asc' else '-'
    
    cursos = cursos.order_by(f'{prefix}{order}')

    return render(
        request,
        'academico/cursos/pesquisar_curso.html',
        {
            'cursos': cursos,
            'q': q,
            'order': order,
            'dir': direction,
            'active_menu': 'cursos',
        }
    )


# Exclui um curso individualmente.
@role_required(['COORDENADOR'])
@login_required
def excluir_curso(request, curso_id):

    curso = get_object_or_404(Curso, pk=curso_id)
    nome_curso = curso.nome
    curso.delete()
    messages.success(request, f'Curso "{nome_curso}" excluído com sucesso!')
    return redirect('pesquisar_curso')


# Exclui múltiplos cursos selecionados via checkbox.
@role_required(['COORDENADOR'])
@login_required
def excluir_cursos_massa(request):

    if request.method == 'POST':
        ids_raw = request.POST.get('curso_ids', '')
        if ids_raw:
            ids_list = ids_raw.split(',')
            count = Curso.objects.filter(pk__in=ids_list).delete()[0]
            messages.success(request, f'{count} cursos excluídos com sucesso!')
    return redirect('pesquisar_curso')


# Exibe os detalhes de um curso em modo somente leitura (visualizar).
@login_required
def informacoes_curso(request, pk):

    curso = get_object_or_404(Curso, pk=pk)
    return render(request, 'academico/cursos/cadastrar_curso.html', {
        'curso': curso,
        'visualizar': True,
        'active_menu': 'cursos'
    })
    curso = get_object_or_404(Curso, pk=pk)
    # Passamos o objeto curso e uma flag 'visualizar' como True
    return render(request, 'academico/cursos/cadastrar_curso.html', {
        'curso': curso,
        'visualizar': True 
    })

#endregion  ---

#region --- TURMAS --- 
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
#endregion ---

#region --- VOLUNTÁRIOS --- 
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
#endregion ---