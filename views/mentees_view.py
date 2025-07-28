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

query_params =  st.query_params

st.write(query_params)