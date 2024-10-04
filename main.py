import streamlit as st
from fetch_runrunit_tasks import fetch_runrunit_tasks
from healthscore_runrunnit_sheets import fetch_runrunit_feedback
from calculo_healthscore import calculate_heathscore

st.markdown(
    """
    <style>
    div.stButton > button {
        display: block;
        margin-left: auto;
        margin-right: auto;
        font-size: 80px;
        padding: 20px 40px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>
    .centered-image {
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.image("img/Logo.png", width=300, caption="", use_column_width=False, output_format="auto", clamp=False, channels="RGB")

st.title("Update Runrunnit Database")

n_pags = st.number_input("Número de páginas", min_value=1, max_value=100, value=20, step=1, format="%d")

if st.button("Executar"):
    fetch_runrunit_tasks(n_pags)
    fetch_runrunit_feedback()
    calculate_heathscore()




