import streamlit as st
from urllib.parse import unquote
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
st.dataframe(df_final)

st.title("Dashboard Individual")

def decode_clinic_name(encoded_str):
    """Decodifica o nome da clínica de forma confiável"""
    try:
        # Decodifica URL e substitui hífens por espaços
        decoded = unquote(encoded_str).replace('-', ' ').title()
        # Corrige possíveis substituições feitas na codificação
        return decoded
    except Exception as e:
        st.error(f"Erro na decodificação: {str(e)}")
        return None

# Exemplo de uso no Streamlit
query_params = st.experimental_get_query_params()
if 'clinic' in query_params:
    clinic_name = decode_clinic_name(query_params['clinic'][0])
    st.success(f"Clínica: {clinic_name}")