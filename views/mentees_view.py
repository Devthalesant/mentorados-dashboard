import streamlit as st
from urllib.parse import unquote
from data_values import *
import pandas as pd
from datetime import date, timedelta
import locale
import matplotlib.pyplot as plt
import plotly.express as px

today = date.today()
tomorrow = today + timedelta(days=1)
year = tomorrow.year
month = tomorrow.month
month_name = tomorrow.strftime("%B")  # Retorna o nome completo do mês


# Pegando os dados
@st.cache_data
def load_data():
    return pegar_dados_google_sheets(month)

# Decodificador simples
def decodificar_nome(codigo):
    return unquote(codigo).replace('-', ' ').title()

# Carrega os dados
df_final = load_data()

if df_final is None or df_final.empty:
    st.warning("Ainda não há dados a serem analisados. Favor Preencher o formulário diário.")
else:
    # Interface do dashboard
    st.title("Dashboard Individual")
    # Obter parâmetro da URL
    query_params = st.query_params

    if 'clinica' in query_params:
        nome_clinica = decodificar_nome(query_params['clinica'])
        
        # Filtro simples no DataFrame
        if 'Clinica' in df_final.columns:
            df_filtrado = df_final[df_final['Clinica'].str.lower() == nome_clinica.lower()]
        
        if df_filtrado is None or df_filtrado.empty:
            st.warning(f"Ainda não há dados a serem analisados sobre a clínica :{nome_clinica}")
            st.warning(f"Favor preenhcer o formulário diário.")
            st.stop()
        
        else:

            df_filtrado["Data"] = pd.to_datetime(df_filtrado["Data"]).dt.strftime('%d/%m/%Y')

        #corrigir os nomes das colunas removendo quebras de linha
        df_filtrado.columns = df_filtrado.columns.str.replace('\n', ' ')

        df_filtrado = df_filtrado.rename(columns={
            "Clinica": "Clinica",
            "Data": "Data",
            "Qual a sua Meta de Faturamento?": "Meta",
            "Leads Gerados no Dia:": "Leads",
            "Avaliações Realizadas no Dia:": "Avaliações",
            "Atendimentos Realizados no dia. (considerando Avaliação)": "Atendimentos",
            "Quantidade de Pedidos Gerados no DIa:": "Pedidos",
            "Valor Vendido no Dia (somente número):": "Valor Vendido"
        })

        # Pegando paramâmetros de Faturamento
        meta = df_filtrado['Meta'].iloc[0]
        meta_formatada = f"R$ {meta:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

        valor_faturado = df_filtrado['Valor Vendido'].sum()
        valor_faturado_formatado = f"R$ {valor_faturado:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

        atingimento_de_meta = valor_faturado/meta *100
        atingimento_de_meta_formatado = f"{atingimento_de_meta:.2f}%"

        valor_remanescente = meta - valor_faturado
        valor_remanescente_formatado = f"R$ {valor_remanescente:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

        # ======================
        # KPI's DE FATURAMENTO - VERSÃO APRIMORADA
        # ======================

        st.markdown("## 💰 Performance Financeira")

        # Container principal com borda sutil
        with st.container(border=True):
            # Linha 1: Métricas principais
            cols = st.columns([1,1.2,1])
            
            with cols[0]:
                st.metric(
                    label="**Meta Mensal**",
                    value=meta_formatada,
                    help="Valor total da meta estabelecida"
                )
            
            with cols[1]:
                # Container para os dois KPIs relacionados
                with st.container():
                    st.metric(
                        label="**Faturamento Realizado**",
                        value=valor_faturado_formatado,
                        delta=f"{atingimento_de_meta_formatado} de atingimento",
                        delta_color="normal"
                    )
                    st.metric(
                        label="**Saldo para Meta**",
                        value=valor_remanescente_formatado,
                        help="Valor restante para atingir a meta total"
                    )
            
            with cols[2]:
                # Gráfico de progresso circular (visual)
                progress = min(atingimento_de_meta/100, 1.0)
                st.markdown(f"""
                <div style="text-align: center">
                    <h3 style="margin-bottom: 5px;">Atingimento</h3>
                    <div style="display: inline-block; position: relative; width: 120px; height: 120px;">
                        <svg width="120" height="120">
                            <circle cx="60" cy="60" r="50" stroke="#f0f2f6" stroke-width="10" fill="none"/>
                            <circle cx="60" cy="60" r="50" stroke="#4CAF50" stroke-width="10" 
                                stroke-dasharray="314" stroke-dashoffset="{314 * (1 - progress)}" 
                                fill="none" transform="rotate(-90 60 60)"/>
                            <text x="60" y="65" text-anchor="middle" font-size="20" font-weight="bold">
                                {atingimento_de_meta:.1f}%
                            </text>
                        </svg>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Linha 2: Mensagem de status
            if atingimento_de_meta >= 100:
                st.success("""
                🎉 **Meta Superada!**  
                Parabéns pelo excelente desempenho este mês!
                """, icon="🏆")
                st.balloons()
            elif atingimento_de_meta >= 75:
                st.info(f"""
                🔥 **Bom Desempenho!**  
                Você já atingiu {atingimento_de_meta:.1f}% da meta. Continue assim!
                """)
            elif atingimento_de_meta >= 50:
                st.info(f"""
                ⏳ **Meta Parcialmente Atingida**  
                Falta apenas {valor_remanescente_formatado} para bater a meta total!
                """)
            else:
                st.info(f"""
                📊 **Progresso Mensal**  
                Atualmente em {atingimento_de_meta:.1f}% da meta  

                Boas práticas:
                - Monitore seu desempenho diariamente
                - Priorize as atividades de maior impacto
                - Ajuste o ritmo conforme necessário
                """)

        # Estilo CSS customizado
        st.markdown("""
        <style>
            /* Melhora o espaçamento entre métricas */
            [data-testid="stMetric"] {
                padding: 15px 10px;
            }
            /* Destaque para valores principais */
            [data-testid="stMetricValue"] {
                font-size: 1.5rem;
            }
            /* Alinhamento dos labels */
            [data-testid="stMetricLabel"] {
                display: flex;
                justify-content: center;
            }
        </style>
        """, unsafe_allow_html=True)

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

        leads_gerados = df_filtrado['Leads'].sum()
        atendimentos_realizdos = df_filtrado["Atendimentos"].sum()
        aval_realizadas = df_filtrado['Avaliações'].sum()
        Pedidos = df_filtrado['Pedidos'].sum()

        conversao_leads_atendimentos = atendimentos_realizdos/leads_gerados * 100
        conversao_atendimentos_aval = aval_realizadas/atendimentos_realizdos *100
        conversao_aval_pedidos = Pedidos/aval_realizadas * 100

        conversao_leads_atendimentos_f = f"{conversao_leads_atendimentos:.2f}%"
        conversao_atendimentos_aval_f = f"{conversao_atendimentos_aval:.2f}%"
        conversao_aval_pedidos_f = f"{conversao_aval_pedidos:.2f}%"

        # ======================
        # SEÇÃO 1 - VOLUMES BRUTOS
        # ======================
        st.markdown("### 📈 Volume de Atividades")
        cols = st.columns(4)
        with cols[0]: 
            st.metric(
                label="Leads Gerados", 
                value=leads_gerados,
                help="Total de leads captados no período"
            )
        with cols[1]:
            st.metric(
                label="Atendimentos Realizados", 
                value=atendimentos_realizdos,
                help="Total de clientes atendidos"
            )
        with cols[2]:
            st.metric(
                label="Avaliações Concluídas", 
                value=aval_realizadas,
                help="Total de avaliações realizadas"
            )
        with cols[3]:
            st.metric(
                label="Pedidos Gerados", 
                value=Pedidos,
                help="Total de pedidos fechados",
                delta=f"{conversao_aval_pedidos_f} de conversão"  # Adicionei um delta contextual
            )

        # Divisor visual
        st.divider()
        # ======================
        # SEÇÃO 2 - TAXAS DE CONVERSÃO
        # ======================
        st.markdown("### 🔄 Eficiência Operacional")
        cols = st.columns(3)
        with cols[0]: 
            st.metric(
                label="Leads → Atendimentos", 
                value=conversao_leads_atendimentos_f,
                help=f"{leads_gerados} leads → {atendimentos_realizdos} atendimentos"
            )
        with cols[1]:
            st.metric(
                label="Atendimentos → Avaliações", 
                value=conversao_atendimentos_aval_f,
                help=f"{atendimentos_realizdos} atendimentos → {aval_realizadas} avaliações"
            )
        with cols[2]:
            st.metric(
                label="Avaliações → Pedidos", 
                value=conversao_aval_pedidos_f,
                help=f"{aval_realizadas} avaliações → {Pedidos} pedidos"
            )

        # ======================
        # MELHORIAS VISUAIS ADICIONAIS
        # ======================
        st.markdown("""
        <style>
            /* Estilização dos cards de métricas */
            div[data-testid="stMetric"] {
                background-color: #f0f2f6;
                border-radius: 10px;
                padding: 15px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            /* Espaçamento entre seções */
            .section {
                margin-bottom: 30px;
            }
        </style>
        """, unsafe_allow_html=True)

        # ======================
        # GRÁFICO DE FUNIL DE CONVERSÃO
        # ======================
        st.markdown("---")
        st.subheader("📉 Funil de Conversão Completo")

        # Dados para o funil
        funil_data = pd.DataFrame({
            'Estágio': ['Leads', 'Atendimentos', 'Avaliações', 'Pedidos'],
            'Quantidade': [leads_gerados, atendimentos_realizdos, aval_realizadas, Pedidos],
            'Taxa Conversão': [
                '100%',
                f'{conversao_leads_atendimentos:.1f}%',
                f'{conversao_atendimentos_aval:.1f}%',
                f'{conversao_aval_pedidos:.1f}%'
            ]
        })

        # Criar gráfico de funil
        fig_funil = px.funnel(
            funil_data,
            x='Quantidade',
            y='Estágio',
            text='Taxa Conversão',
            color_discrete_sequence=['#7E4EC2'],  # Mantendo seu padrão de cores
            title='<b>Jornada do Cliente</b><br><sub>Da captação ao fechamento</sub>'
        )

        # Ajustes de layout
        fig_funil.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            hovermode='x unified',
            height=500,
            title_x=0.5
        )

        # Exibir no dashboard
        st.plotly_chart(fig_funil, use_container_width=True)









    
    