import streamlit as st
from data_values import *
import pandas as pd
import numpy as np
from datetime import date
import locale

# Configurar locale para português
locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil')

today = date.today()
year = today.year
month = today.month
month_name = today.strftime("%B")  # Retorna o nome completo do mês

# Configurar página em modo wide
st.set_page_config(layout="wide")

st.title("🚀 Dashboard de Performance - 360 Estética")
st.markdown("")
st.divider()    

@st.cache_data
def load_data():
    return pegar_dados_google_sheets()

df_final = load_data()

## 1 Top KPI´s
st.header(f"🎯 Principais KPI's | {month_name.capitalize()}/{year}")
st.markdown("")
top_kpi = Principais_kpis(df_final)

top_kpi = top_kpi.sort_values(by=['Atingimento de Meta (%)'],ascending=False).reset_index(drop=True)

# Função para aplicar estilo
def style_dataframe(df):
    # Formatar colunas numéricas
    df['Meta'] = df['Meta'].map('R${:,.2f}'.format)
    df['Faturamento Total'] = df['Faturamento Total'].map('R${:,.2f}'.format)
    df['Ticket Médio'] = df['Ticket Médio'].map('R${:,.2f}'.format)
    df['Gap/Plus'] = df['Gap/Plus'].map('R${:,.2f}'.format)
    df['Atingimento de Meta (%)'] = df['Atingimento de Meta (%)'].map('{:.2f}%'.format)
    
    # Criar estilo
    styled_df = df.style
        
    styled_df = styled_df.set_properties(**{
        'background-color': '#fafafa'  # branco acinzentado
    }, subset=pd.IndexSlice[::2, :])

    styled_df = styled_df.set_properties(**{
        'background-color': '#f5f5f5'  # cinza muito claro
    }, subset=pd.IndexSlice[1::2, :])
    
    # CORES VIVAS PARA GAP/PLUS (FUNDO)
    def color_gap(val):
        if '-' in val:  # negativo
            return 'background-color: #ff6b6b; color: black'  # vermelho vivo
        else:  # positivo
            return 'background-color: #51cf66; color: black'  # verde vivo
    
    styled_df = styled_df.applymap(color_gap, subset=['Gap/Plus'])
    
    # CORES VIVAS PARA ATINGIMENTO DE META (FUNDO)
    def color_atingimento(val):
        try:
            percent = float(val.strip('%'))
            if percent <= 60:
                return 'background-color: #ff6b6b; color: black'  # vermelho
            else:
                return 'background-color: #51cf66; color: black'  # verde
        except:
            return ''
    
    styled_df = styled_df.applymap(color_atingimento, subset=['Atingimento de Meta (%)'])
    
# MAPA DE CALOR PARA TICKET MÉDIO (FUNDO) - VERSÃO BINÁRIA
    def color_ticket(val):
        try:
            # Converte o valor para float (removendo 'R$' e vírgulas)
            num = float(val.replace('R$', '').replace(',', ''))
            
            # Calcula a média dos tickets médios
            tickets = df['Ticket Médio'].str.replace('R$', '').str.replace(',', '').astype(float)
            media = tickets.mean()
            
            # Define as cores
            if num >= media:
                return 'background-color: #51cf66; color: black'  # verde vibrante
            else:
                return 'background-color: #ff6b6b; color: black'  # vermelho vibrante
        except:
            return ''
    styled_df = styled_df.applymap(color_ticket, subset=['Ticket Médio'])
    
    return styled_df

# Aplicar estilo
styled_top_kpi = style_dataframe(top_kpi.copy())

# Mostrar dataframe estilizado
st.dataframe(styled_top_kpi, height=800, width=1200, use_container_width=True)
st.markdown("")
st.divider()  

## 2 Apresentação - Venda diária detalhada
venda_diaria, meta_mentorado = vendas_diarias_mentorados(df_final)

# Transformando a meta por dia em dicionário
meta_dia_dict = meta_mentorado.set_index('Clinica')['Meta_dia_util'].to_dict()

# Função para formatar valores como moeda brasileira
def format_brl(value):
    if pd.isna(value):
        return ""
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Função para aplicar estilos condicionais
def apply_styles(row):
    styles = []
    for col in venda_diaria.columns:
        style = ""
        # Aplicar negrito em todas as células
        style += "font-weight: bold;"
        
        # Aplicar cores condicionais apenas para colunas de clínicas numéricas
        if col in meta_dia_dict and pd.api.types.is_numeric_dtype(venda_diaria[col]):
            if row[col] < meta_dia_dict[col]:
                style += "background-color: #ff6b6b;"  # Vermelho
            else:
                style += "background-color: #51cf66;"  # Verde
        styles.append(style)
    return styles

# Preparar o DataFrame estilizado
styled_df = (
    venda_diaria.style
    .apply(apply_styles, axis=1)
    .format({col: format_brl for col in venda_diaria.select_dtypes(include=np.number)})
)

# Mostrar o DataFrame formatado
st.header(f"💲Vendas Diárias Detalhadas | {month_name.capitalize()}/{year}")
st.markdown("")
st.dataframe(
    styled_df,
    use_container_width=True)
st.markdown("")
st.divider() 

### 3 - Funil
st.header(f"📊 Funil de Conversão | {month_name.capitalize()}/{year}")
st.markdown("---")  # Separador visual

lista_de_funis = gerando_funil_mentorados(df_final)
metricas_para_formatar = ['Ticket Médio', 'Faturamento Total']

# Calculate number of rows needed (3 funnels per row)
num_funis = len(lista_de_funis)
num_rows = (num_funis + 2) // 3  # Round up division

for row in range(num_rows):
    cols = st.columns(3)  # Create 3 columns for each row
    
    for col_idx in range(3):
        funil_idx = row * 3 + col_idx  # Aqui usamos inteiros puros
        if funil_idx < num_funis:
            df_funil = lista_de_funis[funil_idx].copy()
            clinic_name = df_funil.at[0,'Valor']
            
            # Verificamos se as colunas necessárias existem
            if not df_funil.empty and all(col in df_funil.columns for col in ['Métrica', 'Valor']):
                for idx in df_funil.index:
                    metrica = df_funil.at[idx, 'Métrica']
                    valor = df_funil.at[idx, 'Valor']
                    atingimento = df_funil.at[idx,'Atingimento']
                    
                    try:
                        if metrica in metricas_para_formatar:
                            # Formata como moeda
                            df_funil.at[idx, 'Valor'] = f"R${float(valor):,.2f}" if str(valor).replace('.','', 1).isdigit() else valor
                        else:
                            df_funil.at[idx,'Valor'] = f"{int(valor)}"

                        if atingimento != "-":
                        # Formata como porcentagem
                            df_funil.at[idx, 'Atingimento'] = f"{float(atingimento):.2f}%" if str(valor).replace('.','', 1).isdigit() else valor
                    except (ValueError, TypeError):
                        pass

            # Aplicar estilo
            styled_funil = df_funil.style \
                .set_properties(**{
                    'background-color': '#f8f9fa',
                    'color': 'black',
                    'font-size': '14px'
                }) \
                .set_table_styles([{
                    'selector': 'th',
                    'props': [
                        ('background-color', '#6a11cb'),
                        ('color', 'white'),
                        ('font-size', '14px'),
                        ('position', 'sticky'),
                        ('top', '0')
                    ]
                }])
            
            with cols[col_idx]:
                with st.container():
                    st.markdown(f"**Clínica {clinic_name}**")
                    st.dataframe(
                        styled_funil,
                        height=min(300, 150 + len(df_funil) * 25),
                        hide_index=True,
                        use_container_width=True
                    )
    
    st.markdown("---")  # Separador entre linhas


