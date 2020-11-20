import pandas as pd
import streamlit as st
from models import *
from view_common import *

def aluno():
    sections = {
        'Inserir aluno': inserir_aluno,
        'Visualizar alunos': visualizar_aluno,
        'Alterar aluno': alterar_aluno,
        'Remover aluno': remover_aluno,
        'Gerenciar disciplinas': gerenciar_disciplinas_aluno
    }

    section = st.sidebar.selectbox("Selecione a opção desejada", tuple(sections.keys()))
    
    sections[section]()

def inserir_aluno():
    st.title('Inserir aluno')

    pnome, unome, cpf, data_nasc, sexo = pega_dados_pessoa()
    curso: Curso = seleciona_entidade(Curso, Curso.nome, 'Curso')

    if curso is None:
        st.warning('Adicione pelo menos um curso.')
        st.stop()

    salvar = st.button('Salvar aluno')

    if salvar:
        valida_nome(pnome, unome)
        valida_tamanho(cpf, 11, message='CPF deve ter 11 dígitos')
        valida_cpf(cpf)

        rga = gera_rga(curso.cod_curso)

        pessoa = Pessoa(rga=rga, pnome=pnome, 
        unome=unome, cpf=cpf, datanasc=data_nasc,
        sexo=sexo)

        try:
            pessoa.save(force_insert=True)

        except Exception as e:
            st.warning('Erro ao salvar. Verifique os dados inseridos')
            st.write(e)
            st.stop()

        aluno = Aluno(rga_aluno=rga, cod_curso=curso.cod_curso)

        #impossível dar erro pois o rga ja está em pessoa,
        # e o curso também existe
        aluno.save(force_insert=True)

        st.success('Registro salvo!')

def visualizar_aluno():
    st.title('Visualizar alunos')

    dados_alunos = list(Pessoa.select(Pessoa.rga, Pessoa.cpf, (Pessoa.pnome + " " + Pessoa.unome).alias('nome'), Curso.nome.alias('nome do curso'),Aluno.cr).join(Aluno).join(Curso).order_by(Pessoa.pnome).dicts())

    if len(dados_alunos) == 0:
        st.warning('Não existem alunos cadastrados')
        st.stop()

    df = pd.DataFrame(dados_alunos).set_index('rga')
    df.round(2)
    
    st.table(df)

def alterar_aluno():
    st.title('Alterar aluno')

    aluno = seleciona_pessoa(Aluno,'Aluno')

    if aluno is None:
        st.warning('Não existem alunos cadastrados')
        st.stop()

    st.title('Dados do aluno')

    pnome, unome, cpf, datanasc, sexo = pega_dados_pessoa(aluno.pessoa.pnome, aluno.pessoa.unome, aluno.pessoa.cpf, aluno.pessoa.datanasc, aluno.pessoa.sexo)
    
    curso_atual = aluno.select().join(Curso)
    cursos = Curso.select().order_by(Curso.cod_curso)

    index = -1
    for c in cursos:
        index += 1
        if c == curso_atual:
            break
   
    curso = st.selectbox('Curso', cursos, format_func=Curso.toString, index=index)

    alterar = st.button('Alterar')

    if alterar:
        valida_nome(pnome, unome)
        valida_tamanho(cpf, 11, message='CPF deve ter 11 dígitos')

        rga = gera_rga(curso.cod_curso)

        pessoa = Pessoa.get_by_id(aluno.pessoa)

        pessoa.pnome = pnome
        pessoa.unome = unome
        pessoa.cpf = cpf
        pessoa.datanasc = datanasc
        pessoa.sexo = sexo

        try:
            pessoa.save()

        except Exception as e:
            st.warning('Erro ao salvar. Verifique os dados inseridos')
            st.write(e)
            st.stop()

        aluno.cod_curso = curso.cod_curso

        aluno.save()

        st.success('Registros alterados!')   
     
def remover_aluno():
    aluno = seleciona_pessoa(Aluno,'Aluno')

    if aluno is None:
        st.warning('Não existem alunos cadastrados')
        st.stop()

    dados_alunos = list(Pessoa.select(Pessoa.rga, Pessoa.cpf, (Pessoa.pnome + " " + Pessoa.unome).alias('nome'), Curso.nome.alias('nome do curso')).join(Aluno).join(Curso).where(Pessoa.rga==aluno.pessoa).order_by(Pessoa.pnome).dicts())

    df = pd.DataFrame(dados_alunos).set_index('rga')

    st.table(df)

    remover = st.button('Remover')

    if remover:
        Pessoa.delete_by_id(aluno.pessoa)

        st.success('Aluno removido com sucesso!')        

def gerenciar_disciplinas_aluno():
    sections = {
        'Matricular aluno': matricular_aluno,
        'Visualizar disciplinas': visualizar_disciplinas,
        'Desmatricular aluno': desmatricular_aluno
    }

    section = st.sidebar.selectbox("Selecione a opção desejada", tuple(sections.keys()))
    
    sections[section]()

def matricular_aluno():
    st.title('Matricular aluno')

    aluno = seleciona_pessoa(Aluno,'Aluno')

    if aluno is None:
        st.warning('Não existem alunos cadastrados')
        st.stop()

    disciplinas_aluno = (Disciplina.select(Disciplina.cod_disciplina)
    .join(AlunoDisc)
    .where(AlunoDisc.rga_aluno==aluno.pessoa))

    disciplinas_matricula = (Disciplina.select()
    .where(Disciplina.cod_disciplina.not_in(disciplinas_aluno)))

    disciplina = st.selectbox('Disciplina', disciplinas_matricula, format_func=Disciplina.toString)

    if disciplinas_aluno is None:
        st.warning('Todas as disciplinas estão vazias')
        st.stop()

    if disciplina is None:
        st.warning('O aluno já está matriculado em todas as disciplinas.')
        st.stop()

    matricular = st.button('Matricular')

    if matricular:
        aluno_disc = AlunoDisc(rga_aluno=aluno.pessoa,cod_disciplina=disciplina.cod_disciplina,nota1=0.0,nota2=0.0,nota3=0.0,frequencia=0.0)
        
        try:
            aluno_disc.save(force_insert=True)
        except Exception as e:
            st.warning('Erro ao salvar. Verifique os dados inseridos')
            st.write(e)
            st.stop()

        st.success('Aluno matriculado!')

def visualizar_disciplinas():
    st.title('Visualizar disciplinas do aluno')  

    aluno = seleciona_pessoa(Aluno,'Aluno')

    if aluno is None:
        st.warning('Não existem alunos cadastrados')
        st.stop()        

    aluno_discs = list(Aluno.select(
    Disciplina.cod_disciplina, Disciplina.nome,
    AlunoDisc.nota1, AlunoDisc.nota2, AlunoDisc.nota3, AlunoDisc.frequencia)
    .join(AlunoDisc, on=(Aluno.pessoa==AlunoDisc.aluno))
    .join(Disciplina, on=(AlunoDisc.cod_disciplina==Disciplina.cod_disciplina))
    .where(Aluno.pessoa==aluno.pessoa)
    .dicts())

    if len(aluno_discs) == 0:
        st.warning('O aluno não está matriculado em nenhuma disciplina')
        st.stop()

    df = pd.DataFrame(aluno_discs).set_index('cod_disciplina')
    st.table(df)

def desmatricular_aluno():
    st.title('Desmatricular aluno')

    aluno: Aluno = seleciona_pessoa(Aluno,'Aluno')

    if aluno is None:
        st.warning('Não existem alunos cadastrados')
        st.stop()

    disciplinas_aluno = (Disciplina.select(Disciplina.cod_disciplina, 
    Disciplina.nome)
    .join(AlunoDisc)
    .where(AlunoDisc.rga_aluno==aluno.pessoa))

    disciplina: Disciplina = st.selectbox('Disciplinas', disciplinas_aluno, format_func=Disciplina.toString)

    if disciplina is None:
        st.warning('O aluno não está matriculado em nenhuma disciplina')
        st.stop()

    desmatricular = st.button('Desmatricular')

    if desmatricular:
        AlunoDisc.delete_by_id([aluno.pessoa, disciplina.cod_disciplina])
        st.success('Aluno desmatriculado')