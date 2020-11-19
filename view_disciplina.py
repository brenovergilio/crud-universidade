import pandas as pd
import streamlit as st
from models import *
from view_common import *

def disciplina():
    sections = {
        'Inserir disciplina': inserir_disciplina,
        'Visualizar disciplinas': visualizar_disciplina,
        'Alterar disciplina': alterar_disciplina,
        'Remover disciplina': remover_disciplina,
        #'Gerenciar disciplinas': gerenciar_disciplinas_aluno
    }

    section = st.sidebar.selectbox("Selecione a opção desejada", tuple(sections.keys()))
    
    sections[section]()

def inserir_disciplina():
    st.title('Inserir disciplina')

    cod_disciplina, nome, carga_horaria, rga_prof = pega_dados_disciplina()

    if rga_prof is None:
        st.write('_O curso deve ter um coordenador._')
        st.stop()

    salvar = st.button('Salvar disciplina')

    if salvar:
        valida_tamanho_minmax(dado=cod_disciplina, min=4, max=8, message='Código precisa ter entre 4 e 8 caracteres')
        valida_tamanho_minmax(dado=nome, min=4, max=40, message='Nome precisa ter entre 4 e 40 caracteres')
        valida_cod_disc(cod_disciplina)
        valida_carga_horaria(carga_horaria)

        disciplina = Disciplina(cod_disciplina=cod_disciplina,nome=nome,carga_horaria=carga_horaria,rga_prof=rga_prof.pessoa.rga)

        try:
            disciplina.save(force_insert=True)

        except Exception as e:
            st.warning('Erro ao salvar. Verifique os dados inseridos')
            st.write(e)
            st.stop()

        st.success('Registro salvo!')

def visualizar_disciplina():
    st.title('Visualizar disciplinas')

    disciplinas = list(Disciplina.select(Disciplina.cod_disciplina, Disciplina.nome.alias('nome da disciplina'), Pessoa.rga.alias('rga do professor'), (Pessoa.pnome + " " + Pessoa.unome).alias('nome do professor')).join(Pessoa,on=(Disciplina.rga_prof==Pessoa.rga)).order_by(Disciplina.cod_disciplina).dicts())

    if len(disciplinas) == 0:
        st.write('_Não há nada por aqui..._')
        st.stop()

    df = pd.DataFrame(disciplinas).set_index('cod_disciplina')

    st.table(df)        

#######nao atualiza no BD
def alterar_disciplina():
    st.title('Alterar disciplina')

    disciplina: Disciplina = seleciona_entidade(Disciplina, Disciplina.nome, 'Disciplina')

    if disciplina is None:
        st.write('_Não há nada por aqui..._')
        st.stop()

    cod_disciplina, nome, carga_horaria, rga_prof = pega_dados_disciplina(cod_disciplina=disciplina.cod_disciplina,nome=disciplina.nome,carga_horaria=disciplina.carga_horaria,rga_prof=disciplina.rga_prof)

    alterar = st.button('Alterar')

    if alterar:
        valida_tamanho_minmax(dado=cod_disciplina, min=4, max=8, message='Código precisa ter entre 4 e 8 caracteres')
        valida_tamanho_minmax(dado=nome, min=4, max=40, message='Nome precisa ter entre 4 e 40 caracteres')
        valida_cod_disc(cod_disciplina)
        valida_carga_horaria(carga_horaria)

        disciplina.cod_disciplina = cod_disciplina
        disciplina.nome = nome
        disciplina.carga_horaria = carga_horaria
        disciplina.rga_prof = rga_prof

        try:
            disciplina.save()

        except Exception as e:
            st.warning('Erro ao salvar. Verifique os dados inseridos')
            st.write(e)
            st.stop()

        st.success('Registros alterados!')  

def remover_disciplina():
    st.title('Remover disciplina')

    disciplina = seleciona_entidade(Disciplina, Disciplina.nome, 'Disciplina')
   
    if disciplina is None:
        st.write('_Não há nada por aqui..._')
        st.stop()

    disciplinas = list(Disciplina.select(Disciplina.cod_disciplina, Disciplina.nome, Pessoa.rga.alias('rga do professor'), (Pessoa.pnome + " " + Pessoa.unome).alias('nome do professor')).join(Pessoa,on=(Disciplina.rga_prof==Pessoa.rga)).where((Pessoa.rga==disciplina.rga_prof) and (Disciplina.cod_disciplina==disciplina.cod_disciplina)).order_by(Disciplina.cod_disciplina).dicts())

    df = pd.DataFrame(disciplinas).set_index('cod_disciplina')

    st.table(df)

    remover = st.button('Remover')

    if remover:

        Disciplina.delete_by_id(disciplina.cod_disciplina)

        st.success('Disciplina removido com sucesso!')