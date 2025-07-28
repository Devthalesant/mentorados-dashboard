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

def decode_clinic_name(encoded_str):
    """Decodifica o nome da clínica de forma confiável"""
    try:
        decoded = unquote(encoded_str).replace('-', ' ').strip().title()
        # Correções manuais para nomes específicos
        corrections = {
            "C": "Clínica",  # Exemplo - ajuste conforme seus dados
            # Adicione outras correções necessárias
        }
        return corrections.get(decoded, decoded)
    except Exception as e:
        st.error(f"Erro na decodificação: {str(e)}")
        return None

# Processa os parâmetros da URL
query_params = st.query_params
st.write("Parâmetros recebidos:", query_params)  # Debug

if 'clinic' in query_params:
    clinic_name = decode_clinic_name(query_params['clinic'][0])
    
    if clinic_name:
        st.success(f"Clínica selecionada: {clinic_name}")
        
        # Filtra o DataFrame
        if 'Clinica' in df_final.columns:
            # Padroniza os nomes para comparação
            df_final['Clinica_Clean'] = df_final['Clinica'].str.strip().str.upper()
            search_name = clinic_name.strip().upper()
            
            # Filtra (com correspondência exata)
            df_filtrado = df_final[df_final['Clinica_Clean'] == search_name]
            
            if not df_filtrado.empty:
                st.write(f"Dados da clínica {clinic_name}:")
                st.dataframe(df_filtrado.drop(columns=['Clinica_Clean']))
            else:
                st.warning(f"Nenhum dado encontrado para: {clinic_name}")
                st.write("Valores únicos na coluna 'Clinica':")
                st.write(df_final['Clinica'].unique())
        else:
            st.error("Coluna 'Clinica' não encontrada no DataFrame!")
            st.write("Colunas disponíveis:", df_final.columns.tolist())
else:
    st.warning("Nenhuma clínica selecionada. Adicione ?clinic=nome-da-clinica à URL")
    st.write("Exemplo: ?clinic=clinica-exemplo")