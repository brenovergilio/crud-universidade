import pandas as pd
import streamlit as st
from models import *
from view_common import *

def curso():
    sections = {
        'Inserir curso': inserir_curso,
        'Visualizar curso': visualizar_curso,
        'Alterar curso': alterar_curso,
        'Remover curso': remover_curso,
        #'Gerenciar disciplinas': gerenciar_disciplinas_aluno
    }

    section = st.sidebar.selectbox("Selecione a opção desejada", tuple(sections.keys()))
    
    sections[section]()

def inserir_curso():
    st.title('Inserir curso')

    cod_curso, prof_coord, nome = pega_dados_curso()

    if prof_coord is None:
        st.warning('Não existem professores cadastrados')
        st.stop()

    salvar = st.button('Salvar curso')

    if salvar:
        valida_nome(nome,)
        valida_tamanho(cod_curso,4,message='Código deve ter 4 dígitos')
        valida_cod_curso(cod_curso)

        curso = Curso(cod_curso=cod_curso,rga_coord=prof_coord.pessoa.rga,nome=nome)

        try:
            curso.save(force_insert=True)

        except Exception as e:
            st.warning('Erro ao salvar. Verifique os dados inseridos')
            st.write(e)
            st.stop()

        st.success('Registro salvo!')

def visualizar_curso():
    st.title('Visualizar cursos')

    cursos = list(Curso.select(Curso.cod_curso, Curso.nome, Pessoa.rga.alias('rga do coordenador'), (Pessoa.pnome + " " + Pessoa.unome).alias('nome do coordenador')).join(Pessoa,on=(Curso.rga_coord==Pessoa.rga)).order_by(Curso.cod_curso).dicts())

    if len(cursos) == 0:
        st.warning('Não existem cursos cadastrados')
        st.stop()

    df = pd.DataFrame(cursos).set_index('cod_curso')

    st.table(df)

def alterar_curso():
    st.title('Alterar curso')

    curso: Curso = seleciona_entidade(Curso, Curso.nome, 'Curso')

    if curso is None:
        st.warning('Não existem cursos cadastrados')
        st.stop()

    cod_curso, prof_coord, nome = pega_dados_curso(cod_curso=curso.cod_curso,prof_coord=curso.rga_coord,nome=curso.nome)

    alterar = st.button('Alterar')

    if alterar:
        valida_nome(nome,)
        valida_tamanho(cod_curso,4,message='Código deve ter 4 dígitos')
        
        if not cod_curso.isdigit():
            st.warning('Código do curso deve ser numérico')
            st.stop()

        dados = {
            Curso.cod_curso: cod_curso,
            Curso.nome: nome
        }

        if curso.rga_coord == prof_coord:
            coord = {Curso.rga_coord : prof_coord}
            dados.update(coord)

        try:
            q = Curso.update(dados).where(Curso.cod_curso==curso.cod_curso)
            q.execute()
        except Exception as e:
            st.warning('Erro ao salvar. Verifique os dados inseridos')
            st.write(e)
            st.stop()

        st.success('Registros alterados!')

def remover_curso():
    curso = seleciona_entidade(Curso, Curso.nome, 'Curso')

    if curso is None:
        st.warning('Não existem cursos cadastrados')
        st.stop()

    cursos = list(Curso.select(Curso.cod_curso, Curso.nome, Pessoa.rga.alias('rga do coordenador'), (Pessoa.pnome + " " + Pessoa.unome).alias('nome do coordenador')).join(Pessoa,on=(Curso.rga_coord==Pessoa.rga)).where((Pessoa.rga==curso.rga_coord) and (Curso.cod_curso==curso.cod_curso)).order_by(Curso.cod_curso).dicts())

    df = pd.DataFrame(cursos).set_index('cod_curso')

    st.table(df)

    remover = st.button('Remover')

    if remover:

        Curso.delete_by_id(curso.cod_curso)

        st.success('Curso removido com sucesso!')