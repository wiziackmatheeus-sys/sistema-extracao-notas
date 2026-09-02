import re
from io import BytesIO

import pandas as pd
import pdfplumber
import streamlit as st


st.set_page_config(
    page_title="Extrator de Notas",
    layout="wide"
)

st.title("Extrator de Notas de Gado")


def ler_pdf(arquivo):
    arquivo.seek(0)
    texto = ""

    with pdfplumber.open(arquivo) as pdf:
        for pagina in pdf.pages:
            texto += (
                pagina.extract_text() or ""
            ) + " "

    return " ".join(texto.split())


def achar(texto, padroes):
    for padrao in padroes:
        resultado = re.search(
            padrao,
            texto,
            re.I
        )

        if resultado:
        
