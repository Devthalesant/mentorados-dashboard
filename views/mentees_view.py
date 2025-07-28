import streamlit as st
from data_values import *
import pandas as pd
import numpy as np
from datetime import date
import locale

# Configuração inicial
today = date.today()
locale.setlocale(locale.LC_TIME, 'pt_BR.utf8')  # Para nomes de mês em português
month_name = today.strftime("%B")

@st.cache_data
def load_data():
    return pegar_dados_google_sheets(today.month)

df_final = load_data()

# Interface principal
st.title("Dashboard Individual")

# Debug dos parâmetros
query_params = st.experimental_get_query_params()  # Alternativa mais compatível
st.write("Parâmetros recebidos:", query_params)

if 'first_key' in query_params:
    try:
        # Decodificação correta dos valores
        code_points = query_params['first_key'][0].split('-')
        decoded_str = ''.join([chr(int(c)) for c in code_points])
        
        # Correção manual de caracteres especiais
        decoded_str = decoded_str.replace('Í', 'Í')  # Corrige o código 205
        
        st.success(f"Clínica decodificada: {decoded_str}")
        
        # Filtro do DataFrame com correspondência exata
        if 'Clinica' in df_final.columns:
            # Remove espaços extras e padroniza
            df_final['Clinica_clean'] = df_final['Clinica'].str.strip().str.upper()
            search_str = decoded_str.strip().upper()
            
            df_filtrado = df_final[df_final['Clinica_clean'] == search_str]
            
            if not df_filtrado.empty:
                st.dataframe(df_filtrado.drop(columns=['Clinica_clean']))
            else:
                st.warning(f"Nenhum dado encontrado para: {decoded_str}")
                st.write("Valores únicos na coluna 'Clinica':")
                st.write(df_final['Clinica'].unique())
        else:
            st.error("Coluna 'Clinica' não encontrada!")
            st.write("Colunas disponíveis:", df_final.columns.tolist())
            
    except Exception as e:
        st.error(f"Erro: {str(e)}")
        st.write("Valor problemático:", query_params['first_key'][0])
else:
    st.warning("Adicione ?first_key=... à URL")
    st.write("Exemplo: ?first_key=67-76-73-78-73-67-65-32-68-82-65-32-74-69-83-83-73-67-65")