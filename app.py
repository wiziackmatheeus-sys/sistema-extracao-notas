import re
from io import BytesIO
import pandas as pd
import pdfplumber
import streamlit as st

st.set_page_config(page_title="Extrator de Notas", layout="wide")
st.title("Extrator de Notas de Gado")


def ler(arquivo):
    arquivo.seek(0)
    with pdfplumber.open(arquivo) as pdf:
        return " ".join(
            " ".join((pagina.extract_text() or "").split())
            for pagina in pdf.pages
        )


def achar(texto, padroes):
    for padrao in padroes:
        resultado = re.search(padrao, texto, re.I)
        if resultado:
            return resultado.group(1).strip(" .,-")
    return ""


def valor(texto):
    padroes = [
        r"VALOR TOTAL DA NOTA\s*([\d.]+,\d{2})",
        r"VALOR TOTAL:\s*R\$\s*([\d.]+,\d{2})",
        r"Valor Líquido:\s*([\d.]+(?:,\d{2})?)",
        r"Valor Original:\s*([\d.]+(?:,\d{2})?)"
    ]

    encontrados = []

    for padrao in padroes:
        encontrados.extend(
            re.findall(padrao, texto, re.I)
        )

    if not encontrados:
        return ""

    numeros = [
        float(item.replace(".", "").replace(",", "."))
        for item in encontrados
    ]

    resultado = f"{max(numeros):,.2f}"

    return (
        resultado
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def extrair(arquivo):
    texto = ler(
