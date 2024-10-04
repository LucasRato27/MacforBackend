import streamlit as st
from fetch_runrunit_tasks import fetch_runrunit_tasks
from healthscore_runrunnit_sheets import fetch_runrunit_feedback
from calculo_healthscore import calculate_heathscore

# Estilos de botão e imagem
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
    .centered-image {
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Exibir o logo
st.image("img/Logo.png", width=300, caption="", use_column_width=False, output_format="auto", clamp=False, channels="RGB")

# Título da aplicação
st.title("Update Runrunnit Database")

# Input para número de páginas
n_pags = st.number_input("Número de páginas", min_value=1, max_value=100, value=20, step=1, format="%d")

# Botão para executar as funções
if st.button("Executar"):
    try:
        # Executar as funções
        fetch_runrunit_tasks(n_pags)
        fetch_runrunit_feedback()
        calculate_heathscore()

        # Exibir mensagem de sucesso
        st.success("Execução concluída com sucesso!")
    except Exception as e:
        # Exibir mensagem de erro em caso de falha
        st.error(f"Ocorreu um erro durante a execução: {e}")
