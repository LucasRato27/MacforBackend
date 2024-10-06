import streamlit as st
from fetch_runrunit_tasks import fetch_runrunit_tasks
from healthscore_runrunnit_sheets import fetch_runrunit_feedback
from calculo_healthscore import calculate_heathscore

# Estilos de CSS para alterar o fundo para preto e o texto para branco, além de ajustar o botão
st.markdown(
    """
    <style>
    /* Estilo da página */
    body { background-color: black; color: white; }
    .stApp { background-color: black; }
    h1, h2, h3, h4, h5, h6, p, div, span { color: white !important; }
    div.stButton > button {
        font-size: 80px;
        padding: 20px 40px;
        background-color: #333333;
        color: white;
        border: 2px solid white;
        border-radius: 10px;
    }
    div.stButton > button:focus { background-color: #555555; color: white; }
    input { background-color: #333333; color: white; border: 1px solid white; }
    </style>
    """,
    unsafe_allow_html=True
)

st.image("img/Logo.png", width=300)

st.title("Update Runrunnit Database")

n_pags = st.number_input("Número de páginas", min_value=1, max_value=100, value=20, step=1)

# Adicionando uma flag de controle
automated_execution = True  # Você pode mudar para 'False' se precisar do controle manual.

if automated_execution:
    fetch_runrunit_tasks(n_pags)
    fetch_runrunit_feedback()
    calculate_heathscore()
else:
    if st.button("Executar"):
        fetch_runrunit_tasks(n_pags)
        fetch_runrunit_feedback()
        calculate_heathscore()
