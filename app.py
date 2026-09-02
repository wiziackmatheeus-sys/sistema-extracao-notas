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


def texto_pdf(arquivo):
    arquivo.seek(0)

    with pdfplumber.open(arquivo) as pdf:
        return " ".join(
            (pagina.extract_text() or "")
            for pagina in pdf.pages
        )


def buscar(texto, padroes):
    for padrao in padroes:
        resultado = re.search(
            padrao,
            texto,
            re.I
        )

        if resultado:
            return resultado.group(1).strip(
                " .,-"
            )

    return ""


def valor_total(texto):
    padroes = [
        r"VALOR TOTAL DA NOTA\s*([\d.]+,\d{2})",
        r"VALOR TOTAL:\s*R\$\s*([\d.]+,\d{2})",
        r"Valor Líquido:\s*([\d.]+(?:,\d{2})?)",
        r"Valor Original:\s*([\d.]+(?:,\d{2})?)"
    ]

    encontrados = []

    for padrao in padroes:
        resultados = re.findall(
            padrao,
            texto,
  
