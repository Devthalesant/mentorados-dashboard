import streamlit as st
from data_values import *
import pandas as pd
import numpy as np
from datetime import date
import locale


st.title("Dashboard Individual gentlemen!!!!!!!")

query_params = st.query_params
st.write(query_params)