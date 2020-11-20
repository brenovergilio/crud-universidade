from peewee import *
from datetime import date
from os import remove
from os.path import isfile

db = SqliteDatabase('universidade.db', pragmas= {
    'foreign_keys': 1
})

class BaseModel(Model):

    def toString(model: Model):
        return ''

    class Meta:
        database = db

#Tabelas do BD
class Pessoa(BaseModel):
    rga = CharField(12, primary_key=True)
    pnome = CharField(20)
    unome = CharField(20)
    cpf = CharField(11, unique=True)
    datanasc = DateField()
    sexo = CharField(1, constraints=[Check('sexo in ("M","F")')])

    def toString(pessoa):
        return f'{pessoa.pnome} {pessoa.unome} | {pessoa.rga}'

class Professor(BaseModel):
    pessoa = ForeignKeyField(Pessoa, backref='professores', 
    primary_key = True, db_column='rga_prof', 
    on_delete='CASCADE',on_update='CASCADE')

    titulo = CharField(15, constraints=[Check('titulo in ("Graduado","Pós-Graduado","Mestrado", "Doutorado","Pós-Doutorado")')])
    salario = DecimalField()

    def toString(professor):
        return f'{professor.pessoa.pnome} {professor.pessoa.unome} | {professor.pessoa}'

class Curso(BaseModel):
    cod_curso = CharField(4, primary_key=True)
    rga_coord = ForeignKeyField(Professor, backref='coordena', 
    unique=True, db_column='rga_coord',
    on_delete='CASCADE', on_update='CASCADE')

    nome = CharField(40)

    def toString(curso):
        return f'{curso.nome} | {curso.cod_curso}'

class Aluno(BaseModel):
    pessoa = ForeignKeyField(Pessoa, backref='alunos', 
    primary_key=True, db_column='rga_aluno',
    on_delete='CASCADE', on_update='CASCADE')

    cod_curso = ForeignKeyField(Curso, backref='alunos', 
    db_column='cod_curso',
    on_delete='CASCADE',on_update='CASCADE')

    cr = DecimalField(null=True, default=0)

    def toString(aluno):
        return f'{aluno.pessoa.pnome} {aluno.pessoa.unome} | {aluno.pessoa}'

class Disciplina(BaseModel):
    cod_disciplina = CharField(8, primary_key=True)
    nome = CharField(80, null=True)
    carga_horaria = IntegerField()
    rga_prof = ForeignKeyField(Professor, 
    backref='disciplinas',db_column='rga_prof',
    on_delete='CASCADE',on_update='CASCADE')

    def toString(disciplina):
        return f'{disciplina.nome} | {disciplina.cod_disciplina}'

class AlunoDisc(BaseModel):
    aluno = ForeignKeyField(Aluno,
    backref='turmas', db_column='rga_aluno',
    on_delete='CASCADE', on_update='CASCADE')

    disciplina = ForeignKeyField(Disciplina, null=False,
    backref='alunos', db_column='cod_disciplina',
    on_delete='CASCADE', on_update='CASCADE')

    nota1 = DecimalField()
    nota2 = DecimalField()
    nota3 = DecimalField()
    frequencia = DecimalField()

    class Meta:
        primary_key = CompositeKey('aluno', 'disciplina')

class Log(BaseModel):
    dataOperacao = DateField(default=date.today())
    tipo = CharField(constraints=[Check('tipo in ("U", "D")')])

    class Meta:
        primary_key = False

class PessoaLog(Log):
    rga_old = CharField()
    cpf_old = CharField()

    rga_new = CharField()
    cpf_new = CharField()

class ProfessorLog(Log):
    rga_old = CharField()

    rga_new = CharField()

class AlunoLog(Log):
    rga_old = CharField()
    curso_old = CharField()

    rga_new = CharField()
    curso_new = CharField()

class DisciplinaLog(Log):
    cod_disciplina_old = CharField()
    professor_old = CharField()

    cod_disciplina_new = CharField()
    professor_new= CharField()

class CursoLog(Log):
    cod_curso_old = CharField()
    coordenador_old = CharField()

    cod_curso_new = CharField()
    coordenador_new = CharField()

class AlunoDiscLog(Log):
    aluno_old = CharField()
    disciplina_old = CharField()
    
    aluno_new = CharField()
    disciplina_new = CharField()

def create_tables(override = True):
    if override:
        if isfile('universidade.db'):
            remove('universidade.db')

    with db:
        db.create_tables([
        Pessoa, Aluno, Professor, 
        Curso, Disciplina, AlunoDisc, 
        PessoaLog, AlunoLog, ProfessorLog,
        CursoLog, DisciplinaLog, AlunoDiscLog])

if __name__ == '__main__':
    create_tables()