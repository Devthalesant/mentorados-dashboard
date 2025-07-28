import streamlit as st
from data_values import *
import pandas as pd
import numpy as np
from datetime import date
import locale


import streamlit as st

# Pega os parâmetros da URL (ex: "?67-108-237..." → {"67-108-237...": ""})
query_params = st.experimental_get_query_params()  # Ou st.query_params no Streamlit ≥ 1.29.0

# Extrai o valor do parâmetro (assumindo que a chave é o próprio código)
if query_params:
    codigo_clinica = list(query_params.keys())[0]  # Pega a primeira chave (ex: "67-108-237...")
    st.write(f"Código da clínica: {codigo_clinica}")
    
    # Opcional: Converter de volta para o nome original (ASCII → texto)
    nome_clinica = ''.join([chr(int(c)) for c in codigo_clinica.split('-')])
    st.write(f"Nome da clínica: {nome_clinica}")
else:
    st.warning("Nenhum parâmetro encontrado na URL.")