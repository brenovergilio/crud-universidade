import pandas as pd
import streamlit as st
from peewee import *
from streamlit.caching import clear_cache
from models import *
from random import randint
from datetime import date

def pega_dados_pessoa(pnome = '', unome='', cpf='', datanasc=None, sexo=None):
    col1, col2 = st.beta_columns(2)

    pnome = col1.text_input('Primeiro nome', pnome)

    unome = col2.text_input('Último nome', unome)

    cpf = st.text_input('CPF', cpf)

    datanasc = st.date_input('Data de nascimento (aaaa/mm/dd)', datanasc)

    sexo_index = 0 if sexo == 'M' else 1
    sexo = st.selectbox(label='Sexo',
    options=['Masculino','Feminino'],
    index=sexo_index)[0]
    
    return pnome, unome, cpf, datanasc, sexo

def pega_dados_prof(titulo='', salario=0.0):
    titulo = st.selectbox('Título', ["Graduado","Pós-Graduado","Mestrado", "Doutorado","Pós-Doutorado"])
    salario = st.number_input('Salário', min_value=0.0, value=8000.0, step=250.0)

    return titulo, salario  

def pega_dados_curso(cod_curso='',prof_coord='',nome=''):
    cod_curso = st.text_input('Código do curos', cod_curso)
    prof_coord = seleciona_pessoa(Professor,'Coordenador do curso')
    nome = st.text_input('Nome do curso', nome)

    return cod_curso, prof_coord, nome

def pega_dados_disciplina(cod_disciplina='', nome='', carga_horaria=34, rga_prof=None):

    cod_disciplina = st.text_input('Código da disciplina', cod_disciplina)

    nome = st.text_input('Nome', nome)

    carga_horaria = st.number_input('Carga horária', min_value=34, value=carga_horaria)

    if rga_prof is None:
        index = 0

    else:
        profs = Professor.select(Professor, Pessoa).join(Pessoa).order_by(Pessoa.pnome)

        index = -1
        for prof in profs:
            index += 1
            if rga_prof == prof.pessoa:
                break

    rga_prof = seleciona_pessoa(Professor,'Coordenador', index)

    return cod_disciplina, nome, carga_horaria, rga_prof

def gera_rga(cod_curso=None):
    ano = str(date.today().year)
    pessoas = Pessoa.select()

    if cod_curso is None:
        sufixo = ''.join([str(randint(0, 9)) for i in range(8)])
        rga = ano + str(sufixo)
        
        while not rga_valido(rga, pessoas):
            sufixo = [randint(0, 9) for i in range(4)]
            rga = ano + str(sufixo)

    else:
        sufixo = ''.join([str(randint(0, 9)) for i in range(4)])
        rga = ano + cod_curso + str(sufixo)

        while not rga_valido(rga, pessoas):
            sufixo = [randint(0, 9) for i in range(4)]
            sufixo = ''.join([str(i) for i in sufixo])
            rga = ano + cod_curso + str(sufixo)

    return rga

def rga_valido(rga, pessoas):
    for pessoa in pessoas:
        if rga == pessoa.rga:
            return False

    return True

def valida_tamanho(dado, tamanho, message, max = False):
    
    if len(dado) != tamanho:
        st.warning(message)
        st.stop()

def valida_tamanho_minmax(dado, min, max, message):

    if not (min <= len(dado) <= max):
        st.warning(message)
        st.stop()

def valida_nome_0(nome):

    if len(nome) == 0:
        st.warning('Nome precisa de pelo menos 1 caractere.')
        st.stop()

def valida_nome(*nomes):
    for nome in nomes:
        if any(c.isdigit() for c in nome):
            st.warning('Nome não pode conter números.')
            st.stop()

        if len(nome) == 0:
            st.warning('Nome precisa de pelo menos 1 caractere.')
            st.stop()

def valida_cpf(cpf):
    pessoas = Pessoa.select()

    for pessoa in pessoas:
        pessoa: Pessoa
        if cpf == pessoa.cpf:
            st.warning('Este CPF já existe no banco de dados.')
            st.stop()

def valida_cod_curso(codigo):

    cursos = Curso.select()

    for curso in cursos:
        curso: Curso
        if codigo == curso.cod_curso:
            st.warning('Este código já existe no banco de dados.')
            st.stop()

def valida_cod_disc(codigo):

    discs = Disciplina.select()

    for disc in discs:
        disc: Disciplina
        if codigo == disc.cod_disciplina:
            st.warning('Este código já existe no banco de dados.')
            st.stop()

def valida_carga_horaria(carga_horaria):
    if carga_horaria < 34:
        st.warning('Carga horária mínima é de 34 horas.')
        st.stop()

def valida_aluno_disc(aluno: BaseModel, disciplina: BaseModel):
    alunos_disciplina = list(Disciplina.select(AlunoDisc.rga_aluno, AlunoDisc.cod_disciplina).join(AlunoDisc, on=(Disciplina.cod_disciplina == AlunoDisc.cod_disciplina)).where(disciplina.cod_disciplina==AlunoDisc.cod_disciplina).dicts())
    for i in alunos_disciplina:
        if i['rga_aluno'] == aluno.pessoa.rga and i['cod_disciplina'] == disciplina.cod_disciplina:
            st.warning('Aluno já está matriculado na disciplina')
            st.stop()       


def seleciona_entidade(entidade: BaseModel, order: Field, label: str):
    entidades = entidade.select().order_by(order)

    return st.selectbox(label, entidades, format_func=entidade.toString)

def seleciona_pessoa(entidade: BaseModel, label: str, index=0):
    pessoas = entidade.select(Pessoa, entidade).join(Pessoa).order_by(Pessoa.pnome)

    return st.selectbox(label, pessoas, format_func=entidade.toString, index=index)

def seleciona_aluno_disc(disciplina: Disciplina, label: str, index=0):
    alunos = Aluno.select().join(AlunoDisc).join(Disciplina).where(AlunoDisc.cod_disciplina==disciplina.cod_disciplina)
    
    aluno: Aluno = st.selectbox(label, alunos, index=index, format_func=Aluno.toString)

    if aluno is None:
        st.write('_Não há nada por aqui..._')
        st.stop()

    alunoDisc = AlunoDisc.get_by_id([aluno.rga_aluno, disciplina.cod_disciplina])

    return alunoDisc

def seleciona_disc_prof(professor: Professor, label: str):
    disciplinas = Disciplina.select(Disciplina).join(Professor).where(Professor.pessoa==professor.pessoa)

    disciplina: Disciplina = st.selectbox(label, disciplinas, format_func=Disciplina.toString)

    if disciplina is None:
        st.write('_Não há nada por aqui..._')
        st.stop()

    return disciplina


'''
def seleciona_professor(label: str, index = 0):
    pessoas = Professor.select(Pessoa, Professor).join(Pessoa).order_by(Pessoa.pnome)

    return st.selectbox(label, pessoas, format_func=Professor.toString, index=index)

def seleciona_aluno(label: str):
    pessoas = Aluno.select(Pessoa, Aluno).join(Pessoa).order_by(Pessoa.pnome)

    return st.selectbox(label, pessoas, format_func=Aluno.toString)
'''