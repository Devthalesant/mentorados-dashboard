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

# Decodificador simples
def decodificar_nome(codigo):
    return unquote(codigo).replace('-', ' ').title()

# Carrega os dados
df_final = load_data()

# Interface do dashboard
st.title("Dashboard Individual")
st.write("Dados completos carregados:")
# Obter parâmetro da URL
query_params = st.query_params

if 'clinica' in query_params:
    nome_clinica = decodificar_nome(query_params['clinica'])
    st.write(f"Dashboard da: {nome_clinica}")
    
    # Filtro simples no DataFrame
    if 'Clinica' in df_final.columns:
        df_filtrado = df_final[df_final['Clinica'].str.lower() == nome_clinica.lower()]

    df_filtrado["Data"] = pd.to_datetime(df_filtrado["Data"]).dt.strftime('%d/%m/%Y')

    st.dataframe(df_filtrado)

    meta = df_filtrado['Qual a sua Meta de Faturamento?'].iloc[0]
    meta_formatada = f"R$ {meta:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

    valor_faturado = df_filtrado['Valor Vendido no Dia (somente número):'].sum()
    valor_faturado_formatado = f"R$ {valor_faturado:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

    atingimento_de_meta = valor_faturado/meta *100
    atingimento_de_meta_formatado = f"{atingimento_de_meta:.2f}%"

    st.metric(atingimento_de_meta_formatado)