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
st.write("Parâmetros brutos:", query_params)

if 'first_key' in query_params:
    # Obtém e limpa o parâmetro
    raw_value = query_params['first_key'][0]
    clean_value = raw_value.strip('"')  # Remove aspas se existirem
    
    # Decodificação
    try:
        codes = [int(code) for code in clean_value.split('-')]
        
        # Filtra apenas caracteres ASCII imprimíveis (32-126)
        decoded_str = ''.join(chr(code) for code in codes if 32 <= code <= 126)
        
        st.success(f"Valor decodificado: {decoded_str}")
        
        # Aqui você pode usar o decoded_str para filtrar seu DataFrame
        # df_filtrado = df_final[df_final['clinica'] == decoded_str]
        
    except ValueError:
        st.error("Formato inválido - os valores devem ser números separados por hífen")
else:
    st.warning("Nenhum parâmetro 'first_key' encontrado na URL")
