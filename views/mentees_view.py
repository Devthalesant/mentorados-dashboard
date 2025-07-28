import streamlit as st
from data_values import *
import pandas as pd
import numpy as np
from datetime import date
import locale


st.title("Dashboard Individual gentlemen!!!!!!!")

st.title("Debug de Parâmetros de URL")

# Todas as abordagens
st.write("st.query_params:", st.query_params)
st.write("experimental_get_query_params:", st.experimental_get_query_params())

# Mostrar URL completa (para verificar se os parâmetros estão chegando)
st.write("URL completa:", st.experimental_get_query_string())