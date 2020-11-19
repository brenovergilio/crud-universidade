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
        st.write('_Não há nada por aqui..._')
        st.stop()

    df = pd.DataFrame(professores).set_index('rga')

    st.table(df)

def alterar_professor():
    st.title('Alterar professor')

    prof = seleciona_pessoa(Professor,'Professor')

    if prof is None:
        st.write('_Não há nada por aqui..._')
        st.stop()

    pnome, unome, cpf, datanasc, sexo = pega_dados_pessoa(prof.pessoa.pnome, prof.pessoa.unome, prof.pessoa.cpf, prof.pessoa.datanasc, prof.pessoa.sexo)
    titulo, salario = pega_dados_prof(prof.titulo, prof.salario)

    alterar = st.button('Alterar')

    if alterar:
        valida_nome(pnome, unome, )
        valida_tamanho(cpf, 11, message='CPF deve ter 11 dígitos')

        pessoa = Pessoa.get_by_id(prof.pessoa)

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

        prof.titulo = titulo
        prof.salario = salario

        prof.save()

        st.success('Registros alterados!')

def remover_professor():
    prof = seleciona_pessoa(Professor,'Professor')

    if prof is None:
        st.write('_Não há nada por aqui..._')
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

    professores = Professor.select()

    if professores is None:
        st.write('_Não há nada por aqui..._')
        st.stop()

    professor = st.selectbox('Selecione o professor', professores, format_func=Professor.toString)

    disciplinas = Disciplina.select(Disciplina).join(Professor).where(Professor.pessoa==professor.pessoa)

    if disciplinas is None:
        st.write('_Não há nada por aqui..._')
        st.stop()

    disciplina = st.selectbox('Selecione a disciplina', disciplinas, format_func=Disciplina.toString)

    alunos = Aluno.select(Aluno).join(AlunoDisc).join(Disciplina).where(Aluno.rga_aluno==AlunoDisc.rga_aluno and AlunoDisc.cod_disciplina==disciplina.cod_disciplina)

    if alunos is None:
        st.write('_Não há nada por aqui..._')
        st.stop()

    aluno = st.selectbox('Selecione o aluno', alunos, format_func=Aluno.toString)
    
    alunoDisc = list(AlunoDisc.select(AlunoDisc).join(Aluno).where(aluno.pessoa.rga==AlunoDisc.rga_aluno and disciplina.cod_disciplina==AlunoDisc.cod_disciplina).dicts())
    print(AlunoDisc.select(AlunoDisc).join(Aluno).where(disciplina.cod_disciplina==AlunoDisc.cod_disciplina and aluno.pessoa.rga==AlunoDisc.rga_aluno))
    for i in range(0,len(alunoDisc)):
        print(alunoDisc[i]['rga_aluno']+alunoDisc[i]['cod_disciplina']+" "+str(i))
    col1,col2,col3 = st.beta_columns(3)
    nota1 = col1.number_input(label='Primeira nota',min_value=0.0,max_value=10.0,value=float(alunoDisc[0]['nota1']),step=0.5)
    nota2 = col2.number_input(label='Segunda nota',min_value=0.0,max_value=10.0,value=float(alunoDisc[0]['nota2']),step=0.5)
    nota3 = col3.number_input(label='Terceira nota',min_value=0.0,max_value=10.0,value=float(alunoDisc[0]['nota3']),step=0.5)

    lancar = st.button('Lançar')

    if lancar:
        AlunoDisc.update({AlunoDisc.nota1: nota1, AlunoDisc.nota2: nota2, AlunoDisc.nota3: nota3}).where(AlunoDisc.rga_aluno==alunoDisc[0]['rga_aluno'] and AlunoDisc.cod_disciplina==alunoDisc[0]['cod_disciplina']).execute()
        st.success('Notas lançadas')

def lancar_presenca():
    st.title('Lançar presenças')