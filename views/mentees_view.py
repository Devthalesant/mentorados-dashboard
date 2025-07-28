import streamlit as st
from data_values import *
import pandas as pd
import numpy as np
from datetime import date
import locale

today = date.today()
year = today.year
month = today.month
month_name = today.strftime("%B")  # Retorna o nome completo do mês


@st.cache_data
def load_data():
    return pegar_dados_google_sheets(month)

df_final = load_data()

st.title("Dashboard Individual gentlemen!!!!!!!")

st.title("Debug de Parâmetros de URL")

# Todas as abordagens
st.write("st.query_params:", st.query_params)
st.dataframe(df_final)

query_params = st.query_params

if 'first_key' in query_params:
    # Remove aspas se existirem
    param_value = query_params['first_key'][0].replace('"', '')
    
    # Decodificação segura
    try:
        codes = [int(code) for code in param_value.split('-')]
        decoded_str = ''.join(chr(code) for code in codes if 32 <= code <= 126)  # Filtra apenas caracteres imprimíveis
        st.write("String decodificada:", decoded_str)
    except ValueError:
        st.error("Erro na decodificação - formato inválido")
