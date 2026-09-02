import re
from io import BytesIO

import pandas as pd
import pdfplumber
import streamlit as st


st.set_page_config(
    page_title="Extrator de Notas de Gado",
    layout="wide"
)

st.title("🐂 Extrator de Notas de Gado")
st.write("Envie GTA, Nota Fiscal e Contra Nota em PDF.")


def ler_pdf(arquivo):
    texto = ""

    arquivo.seek(0)

    with pdfplumber.open(arquivo) as pdf:
        for pagina in pdf.pages:
            texto_pagina = pagina.extract_text() or ""
            texto += texto_pagina + "\n"

    return " ".join(texto.split())


def procurar(texto, padroes):
    for padrao in padroes:
        resultado = re.search(
            padrao,
            texto,
            re.IGNORECASE
        )

        if resultado:
            return resultado.group(1).strip(" .,-")

    return ""


def identificar_tipo(texto):
    texto_maiusculo = texto.upper()

    if (
        "GUIA DE TRÂNSITO ANIMAL" in texto_maiusculo
        or "E-GTA" in texto_maiusculo
    ):
        return "GTA"

    if (
        "FATURA:" in texto_maiusculo
        or "ENT MERC REC C/FIM ESP" in texto_maiusculo
    ):
        return "CONTRA NOTA"

    return "NOTA FISCAL"


def extrair_pecuarista(texto, tipo):
    if tipo == "GTA":
        return procurar(
            texto,
            [
                (
                    r"Procedência.*?Nome:\s*(.+?)"
                    r"\s+Estabelecimento:"
                )
            ]
       
