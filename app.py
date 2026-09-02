import re
from io import BytesIO
import pandas as pd
import pdfplumber
import streamlit as st

st.set_page_config(page_title="Extrator de Notas", layout="wide")
st.title("Extrator de Notas de Gado")


def ler_pdf(arquivo):
    arquivo.seek(0)
    texto = ""

    with pdfplumber.open(arquivo) as pdf:
        for pagina in pdf.pages:
            texto += (pagina.extract_text() or "") + " "

    return " ".join(texto.split())


def buscar(texto, padroes):
    for padrao in padroes:
        resultado = re.search(padrao, texto, re.IGNORECASE)

        if resultado:
            return resultado.group(1).strip(" .,-")

    return ""


def buscar_valor(texto):
    padroes = [
        r"VALOR TOTAL DA NOTA\s*([\d.]+,\d{2})",
        r"VALOR TOTAL:\s*R\$\s*([\d.]+,\d{2})",
        r"Valor Líquido:\s*([\d.]+(?:,\d{2})?)",
        r"Valor Original:\s*([\d.]+(?:,\d{2})?)"
    ]

    valores = []

    for padrao in padroes:
        valores += re.findall(
            padrao,
            texto,
            re.IGNORECASE
        )

    if not valores:
        return ""

    numeros = [
        float(item.replace(".", "").replace(",", "."))
        for item in valores
    ]

    maior = f"{max(numeros):,.2f}"

    return (
        maior
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def extrair(arquivo):
    texto = ler_pdf(arquivo)
    maiusculo = texto.upper()
    tipo = "NOTA FISCAL"

    if (
        "E-GTA" in maiusculo
        or "GUIA DE TRÂNSITO ANIMAL" in maiusculo
    ):
        tipo = "GTA"

    elif "FATURA:" in maiusculo:
        tipo = "CONTRA NOTA"

    pecuarista = buscar(
        texto,
        [
            r"Procedência.*?Nome:\s*(.*?)\s+Estabelecimento:",
            r"RECEBEMOS DE\s+(.*?)(?:\s+-\s+OTR|\s+OS PRODUTOS)",
            r"DESTINAT
