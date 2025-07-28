## Dashboard Geral - Mentorados
from data_values import *
import streamlit as st

st.set_page_config(layout="wide")

# --- PAGE SETUP ---
dash_page = st.Page(
    "views/dashboard_mentees.py",
    title="Dashboard Mentorados",
    icon=":material/thumb_up:",
)

mentees_page = st.Page(
    "views/mentees_view.py",
    title="Dashboard Individual",
    icon=":material/thumb_up:",
)
# --- NAVIGATION SETUP [WITHOUT SECTIONS] ---
# pg = st.navigation(pages=[about_page, project_1_page, project_2_page])

# --- NAVIGATION SETUP [WITH SECTIONS]---
pg = st.navigation(
    {
        "Dashboard Geral": [dash_page],
        "Dashboard Individual": [mentees_page],
    }
)

# --- SHARED ON ALL PAGES ---
# st.logo("assets/codingisfun_logo.png")


# --- RUN NAVIGATION ---
pg.run()
