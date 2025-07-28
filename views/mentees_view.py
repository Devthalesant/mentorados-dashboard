import streamlit as st
from urllib.parse import unquote
from data_values import *
import pandas as pd
from datetime import date
import locale

today = date.today()
year = today.year
month = today.month
month_name = today.strftime("%B")  # Retorna o nome completo do mês

@st.cache_data
def load_data():
    return pegar_dados_google_sheets(month)

# Carrega os dados
df_final = load_data()

# Interface do dashboard
st.title("Dashboard Individual")

# Debug: mostra os dados brutos (opcional)
st.write("Dados completos carregados:")
st.dataframe(df_final)

# Decodificador simples
def decodificar_nome(codigo):
    return unquote(codigo).replace('-', ' ').title()

# Obter parâmetro da URL
query_params = st.query_params

if 'clinica' in query_params:
    nome_clinica = decodificar_nome(query_params['clinica'])
    st.write(f"Dashboard da: {nome_clinica}")
    
    # Filtro simples no DataFrame
    if 'Clinica' in df_final.columns:
        df_filtrado = df_final[df_final['Clinica'].str.lower() == nome_clinica.lower()]
        st.dataframe(df_filtrado)