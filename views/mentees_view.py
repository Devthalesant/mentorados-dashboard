import streamlit as st
from data_values import *
import pandas as pd
import numpy as np
from datetime import date
import locale

today = date.today()
year = today.year
month = today.month
month_name = today.strftime("%B")

@st.cache_data
def load_data():
    return pegar_dados_google_sheets(month)

df_final = load_data()

st.title("Dashboard Individual")

# Debug dos parâmetros
query_params = st.query_params
st.write("Parâmetros brutos:", query_params)

if 'first_key' in query_params:
    raw_value = query_params['first_key'][0]
    
    try:
        # Processamento dos códigos
        codes = [int(code) for code in raw_value.split('-')]
        
        # Decodificação estendida para caracteres latinos (incluindo acentos)
        decoded_str = ''.join(chr(code) for code in codes)
        
        st.success(f"Valor decodificado: {decoded_str}")
        
        # Agora filtre seu DataFrame
        if 'Clínica' in df_final.columns:
            df_filtrado = df_final[df_final['Clínica'].str.contains(decoded_str, case=False, na=False)]
            st.dataframe(df_filtrado)
        else:
            st.error("Coluna 'Clínica' não encontrada no DataFrame")
            
    except ValueError as e:
        st.error(f"Erro na decodificação: {str(e)}")
else:
    st.warning("Nenhum parâmetro 'first_key' encontrado na URL")