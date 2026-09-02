import streamlit as st
import pdfplumber
import pandas as pd
import re

st.set_page_config(
    page_title="Extrator de Notas de Gado",
    layout="wide"
)

st.title("🐂 Extrator de Notas de Gado")


def ler_pdf(arquivo):
    texto = ""

    with pdfplumber.open(arquivo) as pdf:
        for pagina in pdf.pages:
            conteudo = pagina.extract_text()

            if conteudo:
                texto += conteudo

    return texto


arquivos = st.file_uploader(
    "Selecione os PDFs",
    type=["pdf"],
    accept_multiple_files=True
)

if arquivos:

    resultados = []

    for arquivo in arquivos:

        texto = ler_pdf(arquivo)

        resultados.append(
            {
                "Arquivo": arquivo.name,
                "Primeiros 100 caracteres": texto[:100]
            }
        )

    st.dataframe(pd.DataFrame(resultados))
