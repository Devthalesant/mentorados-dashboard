import streamlit as st
from urllib.parse import unquote
from data_values import *
import pandas as pd
from datetime import date
import locale
import matplotlib.pyplot as plt

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
# Obter parâmetro da URL
query_params = st.query_params

if 'clinica' in query_params:
    nome_clinica = decodificar_nome(query_params['clinica'])
    
    # Filtro simples no DataFrame
    if 'Clinica' in df_final.columns:
        df_filtrado = df_final[df_final['Clinica'].str.lower() == nome_clinica.lower()]

    df_filtrado["Data"] = pd.to_datetime(df_filtrado["Data"]).dt.strftime('%d/%m/%Y')

df_filtrado.rename(columns={"Valor Vendido no Dia (somente número)":"Valor Vendido"})

meta = df_filtrado['Qual a sua Meta de Faturamento?'].iloc[0]
meta_formatada = f"R$ {meta:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

valor_faturado = df_filtrado['Valor Vendido'].sum()
valor_faturado_formatado = f"R$ {valor_faturado:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

atingimento_de_meta = valor_faturado/meta *100
atingimento_de_meta_formatado = f"{atingimento_de_meta:.2f}%"

valor_remanescente = meta - valor_faturado
valor_remanescente_formatado = f"R$ {valor_remanescente:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

st.header("💵 KPI´s de Faturamento:")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(f"Meta do mês:",meta_formatada)
with col2:
    st.metric(f"Faturamento Total:",valor_faturado_formatado)
    st.metric("Valor faltando para Gritar Meta:",valor_remanescente_formatado)
with col3:
    st.metric("Atingimento:",atingimento_de_meta_formatado)

if atingimento_de_meta >= 100:
    st.success("🏆 Parabens, Você atingiu a sua Meta do Mês!!! ")
    st.balloons()
elif atingimento_de_meta >= 50:
    st.success(f"💪 Ja Passamos da metade, vamos atrás dos {meta_formatada}")

elif atingimento_de_meta < 50:
    st.warning(f"""
⚡ **Foco Total Necessário!**
    
    Atingimos apenas {atingimento_de_meta_formatado} da meta...
    Mas toda jornada começa com o primeiro passo!
    
    💡 Dica: Revise suas estratégias e mantenha a consistência!
    """)

## Gráfico de Vendas Diárias: 
## Converter datas com o parâmetro dayfirst
df_filtrado["Data"] = pd.to_datetime(df_filtrado["Data"], dayfirst=True, errors='coerce')
df_filtrado = df_filtrado.dropna(subset=['Data'])

# Gráfico simples do Streamlit
st.bar_chart(
    df_filtrado.set_index('Data')['Valor Vendido'],
    color="#724CAF"
)
st.markdown("")
st.divider() 

st.header("🎣 KPI´s de Leads e Agendamentos:")





    
    