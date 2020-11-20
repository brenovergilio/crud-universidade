import pandas as pd
import streamlit as st
from models import *
from view_common import *

def professor():
    sections = {
        'Inserir professor': inserir_professor,
        'Visualizar professores': visualizar_professor,
        'Alterar professor': alterar_professor,
        'Remover professor': remover_professor,
        'Gerenciar disciplinas': gerenciar_disciplinas_professor
    }

    section = st.sidebar.selectbox("Selecione a opção desejada", tuple(sections.keys()))
    
    sections[section]()

def inserir_professor():
    st.title('Inserir professor')

    pnome, unome, cpf, data_nasc, sexo = pega_dados_pessoa()
    titulo, salario = pega_dados_prof()

    salvar = st.button('Salvar professor')

    if salvar:
        valida_nome(pnome, unome, )
        valida_tamanho(cpf, 11, message='CPF deve ter 11 dígitos')
        valida_cpf(cpf)

        rga = gera_rga()

        pessoa = Pessoa(rga=rga, pnome=pnome, 
        unome=unome, cpf=cpf, datanasc=data_nasc,
        sexo=sexo)

        try:
            pessoa.save(force_insert=True)

        except Exception as e:
            st.warning('Erro ao salvar. Verifique os dados inseridos')
            st.write(e)
            st.stop()

        professor = Professor(rga_prof=rga, 
        titulo=titulo, salario=salario)

        #impossível dar erro pois o rga ja está em pessoa,
        # e o título está predefinido
        professor.save(force_insert=True)

        st.success('Registro salvo!')

def visualizar_professor():
    st.title('Visualizar professores')

    professores = list(Professor.select(Pessoa.rga, Pessoa.cpf, Pessoa.datanasc.alias('data de nascimento') ,(Pessoa.pnome + " " + Pessoa.unome).alias('nome'), Professor.titulo, Professor.salario).join(Pessoa).order_by(Pessoa.pnome).dicts())

    if len(professores) == 0:
        st.warning('Não existem professores cadastrados')
        st.stop()

    df = pd.DataFrame(professores).set_index('rga')

    st.table(df)

def alterar_professor():
    st.title('Alterar professor')

    prof = seleciona_pessoa(Professor,'Professor')

    if prof is None:
        st.warning('Não existem professores cadastrados')
        st.stop()

    pnome, unome, cpf, datanasc, sexo = pega_dados_pessoa(prof.pessoa.pnome, prof.pessoa.unome, prof.pessoa.cpf, prof.pessoa.datanasc, prof.pessoa.sexo)
    titulo, salario = pega_dados_prof(prof.titulo, prof.salario)
    rga = st.text_input('RGA',prof.pessoa)
    alterar = st.button('Alterar')

    if alterar:
        valida_nome(pnome, unome, )
        valida_tamanho(cpf, 11, message='CPF deve ter 11 dígitos')

        pessoa = Pessoa.get_by_id(prof.pessoa)
        dados = {
            Pessoa.pnome : pnome,
            Pessoa.unome : unome,
            Pessoa.cpf : cpf,
            Pessoa.datanasc : datanasc,
            Pessoa.sexo : sexo,
            Pessoa.rga : rga
        }
        try:
            q = Pessoa.update(dados).where(Pessoa.rga==pessoa.rga)
            q.execute()
        except Exception as e:
            st.warning('Erro ao salvar. Verifique os dados inseridos')
            st.write(e)
            st.stop()

        dados={
            Professor.titulo : titulo,
            Professor.salario : salario
        }
        

        q = Professor.update(dados).where(Professor.pessoa==pessoa.rga)
        q.execute()

        st.success('Registros alterados!')

def remover_professor():
    prof = seleciona_pessoa(Professor,'Professor')

    if prof is None:
        st.warning('Não existem professores cadastrados')
        st.stop()

    dados_prof = list(Professor.select(Pessoa.rga, Pessoa.cpf, Pessoa.datanasc.alias('data de nascimento'), Pessoa.sexo, (Pessoa.pnome+ " " + Pessoa.unome).alias('nome'), Professor.titulo, Professor.salario).join(Pessoa).where(Professor.pessoa == prof.pessoa).order_by(Pessoa.pnome).dicts())

    df = pd.DataFrame(dados_prof).set_index('rga')

    st.table(df)

    remover = st.button('Remover')

    if remover:
        Pessoa.delete_by_id(prof.pessoa)

        st.success('Professor removido com sucesso!')

def gerenciar_disciplinas_professor():
    sections = {
        'Lançar notas': lancar_notas,
        'Lançar presença': lancar_presenca
    }

    section = st.sidebar.selectbox("Selecione a opção desejada", tuple(sections.keys()))
    
    sections[section]()

def lancar_notas():
    st.title('Lançar notas')

    professor: Professor = seleciona_pessoa(Professor, 'Selecione o professor')

    if professor is None:
        st.warning('Não existem professores cadastrados')
        st.stop()

    disciplina: Disciplina = seleciona_disc_prof(professor, 'Selecione a disciplina')

    if disciplina is None:
        st.warning('Não existem disciplinas cadastradas')
        st.stop()

    aluno_disc: AlunoDisc = seleciona_aluno_disc(disciplina, 'Selecione o aluno')

    if aluno_disc is None:
        st.warning('As disciplinas estão vazias')
        st.stop()

    col1,col2,col3 = st.beta_columns(3)

    nota1 = col1.number_input(label='Primeira nota',min_value=0.0,max_value=10.0,value=float(aluno_disc.nota1),step=0.5)
    
    nota2 = col2.number_input(label='Segunda nota',min_value=0.0,max_value=10.0,value=float(aluno_disc.nota2),step=0.5)
    
    nota3 = col3.number_input(label='Terceira nota',min_value=0.0,max_value=10.0,value=float(aluno_disc.nota3),step=0.5)

    lancar = st.button('Lançar')

    if lancar:
        aluno_disc.nota1 = nota1
        aluno_disc.nota2 = nota2
        aluno_disc.nota3 = nota3
        aluno_disc.save()
        st.success('Notas lançadas')

def lancar_presenca():
    st.title('Lançar presenças')

    professor: Professor = seleciona_pessoa(Professor, 'Selecione o professor')

    if professor is None:
        st.warning('Não existem professores cadastrados')
        st.stop()

    disciplina: Disciplina = seleciona_disc_prof(professor, 'Selecione a disciplina')

    if disciplina is None:
        st.warning('Não existem disciplinas cadastradas')
        st.stop()

    aluno_disc: AlunoDisc = seleciona_aluno_disc(disciplina, 'Selecione o aluno')

    if aluno_disc is None:
        st.warning('As disciplinas estão vazias')
        st.stop()

    frequencia = st.number_input('Horas de presença', min_value=0, max_value=disciplina.carga_horaria, value=int(aluno_disc.frequencia), step=2)

    lancar = st.button('Lançar')

    if lancar:
        aluno_disc.frequencia = frequencia
        aluno_disc.save()
        st.success('Frequência lançada')