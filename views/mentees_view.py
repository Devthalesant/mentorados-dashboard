import streamlit as st
from urllib.parse import unquote
from data_values import *
import pandas as pd
from datetime import date
import locale

# Configuração inicial
today = date.today()
locale.setlocale(locale.LC_TIME, 'pt_BR.utf8')  # Para nomes de mês em português
month_name = today.strftime("%B")

@st.cache_data
def load_data():
    return pegar_dados_google_sheets(today.month)

# Carrega os dados
df_final = load_data()

# Interface do dashboard
st.title("Dashboard Individual")

# Debug: mostra os dados brutos (opcional)
st.write("Dados completos carregados:")
st.dataframe(df_final)

import streamlit as st
from urllib.parse import unquote

# Decodificador simples
def decodificar_nome(codigo):
    return unquote(codigo).replace('-', ' ').title()

# Obter parâmetro da URL
query_params = st.query_params

if 'clinica' in query_params:
    nome_clinica = decodificar_nome(query_params['clinica'][0])
    st.write(f"Dashboard da: {nome_clinica}")
    
    # Filtro simples no DataFrame
    if 'Clinica' in df_final.columns:
        df_filtrado = df_final[df_final['Clinica'].str.lower() == nome_clinica.lower()]
        st.dataframe(df_filtrado)