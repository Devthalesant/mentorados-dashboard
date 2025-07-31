import streamlit as st
from data_values import *
import pandas as pd
import numpy as np
from datetime import date
import locale

# Configurar locale para português
try:
    locale.setlocale(locale.LC_TIME, 'pt-BR')
except locale.Error:
    print("Locale 'Portuguese_Brazil' not supported on this system.")
    # Apply a fallback or handle accordingly

today = date.today()
year = today.year
month = today.month
month_name = today.strftime("%B")  # Retorna o nome completo do mês

# Variável de controle de autenticação
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

# Parte de senha
if not st.session_state['autenticado']:
    senha_correta = "Mentorados360"
    senha_usuario = st.text_input("Digite a senha para acessar este dashboard:", type="password")
    if senha_usuario == senha_correta:
        st.session_state['autenticado'] = True
        st.rerun()
    else:
        if senha_usuario:  # usuário tentou inserir alguma senha
            st.error("Pa Acesso Negado!")
            st.image("image.jpg",use_column_width=True)
        st.stop()  # interrompe a execução até que a senha seja correta

else:
    # Configurar página em modo wide
    st.set_page_config(layout="wide")

    st.title("🚀 Dashboard de Performance - 360 Estética")
    st.markdown("")
    st.divider()    

    @st.cache_data
    def load_data():
        return pegar_dados_google_sheets(month)

    df_final = load_data()

    ## 1 Top KPI´s
    st.header(f"🎯 Principais KPI's | {month_name.capitalize()}/{year}")
    st.markdown("")
    st.write(month)
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

    # Função para estilizar o cabeçalho da tabela com cor roxa clara
    def style_header(df_style):
        return df_style.set_table_styles([
            {
                'selector': 'thead th',
                'props': [('background-color', '#D8BFD8'),  # Roxo claro
                        ('color', 'black')]
            }
        ])

    # Configurações iniciais
    st.header(f"📊 Funil de Conversão | {month_name.capitalize()}/{year}")
    st.markdown("---")

    # Constantes e configurações
    METRICAS_PARA_FORMATAR = ['Ticket Médio', 'Faturamento Total']
    COLORS = {
        'bad': 'red',
        'good': 'green',
        'header_bg': '#D8BFD8',
        'table_bg': '#f8f9fa'
    }
    METRICA_THRESHOLDS = {
        'Atendimento no Mês': 40,
        'Avaliações no Mês': 40,
        'Pedidos': 50
    }

    # Processamento dos dados
    def formatar_valor(metrica, valor):
        """Formata valores conforme o tipo de métrica"""
        try:
            if metrica in METRICAS_PARA_FORMATAR:
                return f"R${float(valor):,.2f}" if str(valor).replace('.', '', 1).isdigit() else valor
            return f"{int(valor)}" if str(valor).replace('.', '', 1).isdigit() else valor
        except (ValueError, TypeError):
            return valor

    def formatar_atingimento(atingimento):
        """Formata porcentagem de atingimento"""
        try:
            return f"{float(atingimento):.2f}%" if atingimento != "-" else atingimento
        except (ValueError, TypeError):
            return atingimento

    def aplicar_estilo_atingimento(metrica, atingimento_str):
        """Aplica cor condicional ao atingimento"""
        try:
            atingimento = float(atingimento_str.strip('%'))
            threshold = METRICA_THRESHOLDS.get(metrica)
            if threshold is not None:
                color = COLORS['good'] if atingimento >= threshold else COLORS['bad']
                return f"<span style='color:{color}'>{atingimento_str}</span>"
        except (ValueError, AttributeError):
            pass
        return atingimento_str

    def estilizar_tabela(df):
        """Aplica estilos à tabela"""
        return df.style \
            .set_properties(**{
                'background-color': COLORS['table_bg'],
                'color': 'black',
                'font-size': '14px'
            }) \
            .set_table_styles([{
                'selector': 'th',
                'props': [
                    ('background-color', COLORS['header_bg']),
                    ('color', 'black'),
                    ('font-size', '14px'),
                    ('position', 'sticky'),
                    ('top', '0')
                ]
            }])

    # Loop principal otimizado
    lista_de_funis = gerando_funil_mentorados(df_final)

    for i in range(0, len(lista_de_funis), 3):
        cols = st.columns(3)
        for col_idx, df_funil in enumerate(lista_de_funis[i:i+3]):
            if df_funil.empty or not all(col in df_funil.columns for col in ['Métrica', 'Valor', 'Atingimento']):
                continue

            clinic_name = df_funil.at[0, 'Valor']
            df_processed = df_funil.copy()

            # Aplicar formatações
            for idx in df_processed.index:
                metrica = df_processed.at[idx, 'Métrica']
                
                # Formatar valores
                df_processed.at[idx, 'Valor'] = formatar_valor(metrica, df_processed.at[idx, 'Valor'])
                
                # Formatar e estilizar atingimento
                df_processed.at[idx, 'Atingimento'] = formatar_atingimento(df_processed.at[idx, 'Atingimento'])
                df_processed.at[idx, 'Atingimento'] = aplicar_estilo_atingimento(
                    metrica, df_processed.at[idx, 'Atingimento']
                )

            # Exibição
            with cols[col_idx]:
                with st.container():
                    st.markdown(f"**Clínica {clinic_name}**")
                    styled_table = estilizar_tabela(df_processed)
                    st.markdown(styled_table.to_html(escape=False), unsafe_allow_html=True)
