import streamlit as st
from urllib.parse import unquote
from data_values import *
import pandas as pd
from datetime import date
import locale
import matplotlib.pyplot as plt
import plotly.express as px

today = date.today()
year = today.year
month = today.month
month_name = today.strftime("%B")  # Retorna o nome completo do mês


# Pegando os dados
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

# Renomeando Coluna de Valor
df_filtrado = df_filtrado.rename(columns={"Valor Vendido no Dia (somente número):":"Valor Vendido",
                                          "Leads Gerados no Dia:" : "Leads",
                                          "Avaliações Realizadas no Dia:" : "Avaliações",
                                          "Atendimentos Realizados no dia.(considerando Avaliação)" : "Atendimentos",
                                          "Quantidade de Pedidos Gerados no DIa:" : "Pedidos",
                                          "Qual a sua Meta de Faturamento?" : "Meta"})


# Pegando paramâmetros de Faturamento
meta = df_filtrado['Meta'].iloc[0]
meta_formatada = f"R$ {meta:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

valor_faturado = df_filtrado['Valor Vendido'].sum()
valor_faturado_formatado = f"R$ {valor_faturado:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

atingimento_de_meta = valor_faturado/meta *100
atingimento_de_meta_formatado = f"{atingimento_de_meta:.2f}%"

valor_remanescente = meta - valor_faturado
valor_remanescente_formatado = f"R$ {valor_remanescente:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

## Mostrando KPI´s
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

## Gráfico de Vendas Diárias com Plotly
st.markdown("---")
st.subheader("📊 Vendas Diárias")

# Converter e ordenar datas
df_filtrado["Data"] = pd.to_datetime(df_filtrado["Data"], dayfirst=True)
df_filtrado = df_filtrado.sort_values("Data")

# Criar gráfico
fig = px.bar(
    df_filtrado,
    x="Data",
    y="Valor Vendido",
    labels={"Valor Vendido": "Valor (R$)", "Data": ""},
    text=[f'R$ {x:,.0f}'.replace(',', '.') for x in df_filtrado['Valor Vendido']],
    color_discrete_sequence=["#7E4EC2"]  # Mesmo roxo do seu estilo
)

# Adicionar linha da média
media = df_filtrado['Valor Vendido'].mean()
fig.add_hline(
    y=media,
    line_dash="dash",
    line_color="#FFA726",
    annotation_text=f"Média: R$ {media:,.2f}".replace('.', '|').replace(',', '.').replace('|', ','),
    annotation_position="bottom right"
)

# Ajustes finais
fig.update_traces(textposition='outside')
fig.update_layout(
    xaxis_tickformat="%d/%m",
    xaxis_tickangle=-45,
    showlegend=False,
    yaxis_gridcolor='rgba(0,0,0,0.1)',
    plot_bgcolor='rgba(0,0,0,0)'
)

# Exibir no Streamlit
st.plotly_chart(fig, use_container_width=True)

st.markdown("")
st.divider() 

st.header("🎣 KPI´s de Leads e Agendamentos:")
st.dataframe(df_filtrado)

leads_gerados = df_filtrado['Leads'].sum()
atendimentos_realizdos = df_filtrado["Atendimentos"].sum()
aval_realizadas = df_filtrado['Avaliações'].sum()
Pedidos = df_filtrado['Pedidos'].sum()


col1,col2,col3 = st.columns(3)

with col1: 
    st.metric(f"Nesse mês você gerou{leads_gerados}")
with col2:
    st.metric(f"Realizou {atendimentos_realizdos} Atendimentos")
with col3:
    st.metric(f"Além de {aval_realizadas} Avaliações")




    
    