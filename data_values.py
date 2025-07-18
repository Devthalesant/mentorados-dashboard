import pandas as pd 
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import calendar
from datetime import date
import holidays
from pandas.tseries.offsets import CustomBusinessDay
import numpy as np
from streamlit_gsheets import GSheetsConnection
import streamlit as st
import time

def load_dataframe(worksheet):

  conn = st.connection("gsheets_2", type=GSheetsConnection)
  df = conn.read(worksheet=worksheet)

  return df

def pegar_dados_google_sheets():
    df_controle = load_dataframe("Aux_clinics")

    list_to_ignore = ["Padrão", "Aux_clinics"]
    df_controle = df_controle.loc[~df_controle["CLÍNICA"].isin(list_to_ignore)]
    lista_mentorados = df_controle["CLÍNICA"].unique().tolist()

    lista_de_dfs = []

    for clinic in lista_mentorados:
        time.sleep(2)  # evita estourar a cota: 60/minuto
        aba_respostas = load_dataframe(clinic)
        aba_respostas["Clinica"] = clinic
        lista_de_dfs.append(aba_respostas)
        print(f"adicionando : {clinic}")

    print("Todas clínicas adicionadas")
    df_final = pd.concat(lista_de_dfs, ignore_index=True)

    df_final_columns = [
        'Clinica', 'Data', 'Qual a sua Meta de Faturamento?', 'Leads Gerados no Dia:',
        'Avaliações Realizadas no Dia:', 'Atendimentos Realizados no dia.\n(considerando Avaliação)',
        'Quantidade de Pedidos Gerados no DIa:', 'Valor Vendido no Dia (somente número):'
    ]

    df_final = df_final[df_final_columns]

    return df_final


def vendas_diarias_mentorados(df_final):
    # Data atual
    today = date.today()
    year = today.year
    month = today.month

    # start date and end date
    start_date = f'{year}-{month:02d}-01'
    end_day = pd.Timestamp(year=year, month=month, day=1).days_in_month
    end_date = f'{year}-{month:02d}-{end_day}'

    # Brazilian holidays
    br_holidays = holidays.CountryHoliday('BR', years=[year])

    # converting the holidays to list
    holiday_dates = list(br_holidays.keys())

    # creating a custom businnes days
    custom_bday = CustomBusinessDay(holidays=holiday_dates, weekmask='Mon Tue Wed Thu Fri Sat')

    # generate business days
    business_days = pd.date_range(start=start_date, end=end_date, freq=custom_bday)
    num_business_day = len(business_days)

    # groupby to get the sales by day by mentee
    venda_diaria_gp = df_final.groupby(['Clinica','Data']).agg({"Valor Vendido no Dia (somente número):" : 'sum'}).reset_index()

    # treating date values
    venda_diaria_gp['Data'] = pd.to_datetime(venda_diaria_gp['Data'])

    # sorting values by date
    venda_diaria_gp = venda_diaria_gp.sort_values(by=['Data'])

    # tranforming the date for brazilian standard
    venda_diaria_gp['Data'] = venda_diaria_gp['Data'].dt.strftime('%d/%m/%Y')

    # formating the df so the columns can be the dates
    venda_diaria_gp = venda_diaria_gp.pivot_table(index='Data', columns='Clinica', values='Valor Vendido no Dia (somente número):', aggfunc='sum').reset_index()

    # getting the mentee goals 
    metas_por_mentorado = df_final.groupby(['Clinica']).agg({'Qual a sua Meta de Faturamento?' : 'first','Valor Vendido no Dia (somente número):' : 'sum'}).reset_index()

    metas_por_mentorado["Meta_dia_util"] = metas_por_mentorado['Qual a sua Meta de Faturamento?'] / num_business_day

    return venda_diaria_gp, metas_por_mentorado


def Principais_kpis(df_final):
    
    #Principais KPI´s 
    df_data_kpi = df_final.copy()

    df_data_kpi['Vendas Dias ticket'] = df_data_kpi['Valor Vendido no Dia (somente número):']

    df_data_kpi = df_data_kpi.groupby('Clinica').agg({'Qual a sua Meta de Faturamento?':'first',
                                                    'Quantidade de Pedidos Gerados no DIa:' : 'sum',
                                            'Valor Vendido no Dia (somente número):':'sum',
                                            'Vendas Dias ticket' : 'mean',
                                            'Atendimentos Realizados no dia.\n(considerando Avaliação)':'sum',
                                            'Avaliações Realizadas no Dia:' : 'sum',
                                            'Leads Gerados no Dia:' : 'sum'}).reset_index()


    df_data_kpi = df_data_kpi.rename(columns={'Qual a sua Meta de Faturamento?':'Meta',
                                            'Quantidade de Pedidos Gerados no DIa:' : 'Pedidos',
                                    'Valor Vendido no Dia (somente número):' : 'Faturamento Total',
                                    'Vendas Dias ticket' : 'Ticket Médio',
                                    'Atendimentos Realizados no dia.\n(considerando Avaliação)' : "Atendimento No mês",
                                    'Avaliações Realizadas no Dia:' : 'Avaliações no Mês',
                                    'Leads Gerados no Dia:' : 'Leads no Mês'})


    df_top_kpi = df_data_kpi[["Clinica",'Meta','Pedidos','Faturamento Total','Ticket Médio']].copy()

    df_top_kpi['Gap/Plus'] = df_top_kpi['Faturamento Total'] - df_top_kpi['Meta']

    df_top_kpi['Atingimento de Meta (%)'] = df_top_kpi['Faturamento Total'] / df_top_kpi['Meta'] * 100

    df_top_kpi['Atingimento de Meta (%)'] = df_top_kpi['Atingimento de Meta (%)'].round(2)
    df_top_kpi['Ticket Médio'] = df_top_kpi['Ticket Médio'].round(2)

    return df_top_kpi

def gerando_funil_mentorados(df_final):
    # Funil: 
    df_data_funil = df_final.copy()

    df_data_funil['Vendas Dias ticket'] = df_data_funil['Valor Vendido no Dia (somente número):']

    df_data_funil = df_data_funil.rename(columns={
        'Qual a sua Meta de Faturamento?': 'Meta',
        'Quantidade de Pedidos Gerados no DIa:': 'Pedidos',
        'Valor Vendido no Dia (somente número):': 'Faturamento Total',
        'Vendas Dias ticket': 'Ticket Médio',
        'Atendimentos Realizados no dia.\n(considerando Avaliação)': "Atendimento No mês",
        'Avaliações Realizadas no Dia:': 'Avaliações no Mês',
        'Leads Gerados no Dia:': 'Leads no Mês'
    })

    list_of_clincs = df_data_funil['Clinica'].unique().tolist()

    list_of_funil_df = []

    for c in list_of_clincs:
        df_clinica = df_data_funil[df_data_funil['Clinica'] == c]
        
        # Agrupando por clínica e agregando as principais métricas
        df_agrupado = df_clinica.agg({
            'Leads no Mês': 'sum',
            'Atendimento No mês': 'sum',
            'Avaliações no Mês': 'sum',
            'Pedidos': 'sum',
            'Ticket Médio': 'mean',
            'Faturamento Total': 'sum'
        }).reset_index()
        
        df_agrupado.columns = ['Métrica', 'Valor']
        
        # Adicionando coluna de Atingimento
        df_agrupado['Atingimento'] = '-'
        
        # Calculando as conversões
        for i, row in df_agrupado.iterrows():
            if row['Métrica'] == 'Atendimento No mês':
                leads = df_agrupado[df_agrupado['Métrica'] == 'Leads no Mês']['Valor'].values[0]
                if leads != 0:
                    df_agrupado.at[i, 'Atingimento'] = row['Valor']/leads *100
                    
            elif row['Métrica'] == 'Avaliações no Mês':
                atendimentos = df_agrupado[df_agrupado['Métrica'] == 'Atendimento No mês']['Valor'].values[0]
                if atendimentos != 0:
                    df_agrupado.at[i, 'Atingimento'] = row['Valor']/atendimentos *100
                    
            elif row['Métrica'] == 'Pedidos':
                avaliacoes = df_agrupado[df_agrupado['Métrica'] == 'Avaliações no Mês']['Valor'].values[0]
                if avaliacoes != 0:
                    df_agrupado.at[i, 'Atingimento'] = row['Valor']/avaliacoes *100
        
        # Adicionando a clínica como primeira linha
        clinica_row = pd.DataFrame([['Clinica', c, '-']], columns=['Métrica', 'Valor', 'Atingimento'])
        df_agrupado = pd.concat([clinica_row, df_agrupado], ignore_index=True)
        
        list_of_funil_df.append(df_agrupado)

    # Para acessar o DataFrame formatado da terceira clínica (índice 2)
    return list_of_funil_df

