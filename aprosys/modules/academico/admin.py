from django.contrib import admin
from .models import (
    Curso,
    Turno,
    PeriodoLetivo,
    Turma,
    Disciplina,
    TurmaDisciplina,
    Voluntario,
    Aluno,
    TurmaAluno,
    TurmaDisciplinaProfessor,
    CustomUser
)


# Registra todos os modelos
admin.site.register(CustomUser)
admin.site.register(Curso)
admin.site.register(Turno)
admin.site.register(PeriodoLetivo)
admin.site.register(Turma)
admin.site.register(Disciplina)
admin.site.register(TurmaDisciplina)
admin.site.register(Voluntario)
admin.site.register(Aluno)
admin.site.register(TurmaAluno)
admin.site.register(TurmaDisciplinaProfessor)