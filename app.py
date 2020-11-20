import streamlit as st
from streamlit.caching import clear_cache
from view_aluno import *
from view_professor import *
from view_curso import *
from view_disciplina import *

def run():
    st.sidebar.title('CRUD Universidade')
    

    sections = {
        'Gerenciar alunos': aluno,
        'Gerenciar professores': professor,
        'Gerenciar disciplinas': disciplina,
        'Gerenciar cursos': curso
    }

    st.sidebar.title('Seções')
 
    section = st.sidebar.selectbox("Selecione a opção desejada", tuple(sections.keys()), index=0)

    sections[section]()

    limpar_campos = st.sidebar.button('Limpar campos')
    if limpar_campos:
        clear_cache()

if __name__ == '__main__':
    run()