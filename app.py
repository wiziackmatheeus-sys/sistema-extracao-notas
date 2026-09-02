import streamlit as st
import pdfplumber
import pandas as pd
import re
from io import BytesIO

st.set_page_config(
    page_title="Extrator de Notas de Gado",
    layout="wide"
)

st.title("🐂 Extrator de Notas de Gado")


def ler_pdf(arquivo):
    texto = ""

    try:
        with pdfplumber.open(arquivo) as pdf:
            for pagina in pdf.pages:
                conteudo = pagina.extract_text()

                if conteudo:
                    texto += conteudo + "\n"

    except Exception as erro:
        st.error(f"Erro ao ler {arquivo.name}: {erro}")

    return texto


def buscar(texto, padrao):
    resultado = re.search(
        padrao,
        texto,
        re.IGNORECASE | re.MULTILINE
    )

    if resultado:
        return resultado.group(1).strip()

    return ""


def identificar_tipo(texto):

    texto = texto.upper()

    if "E-GTA" in texto or "GUIA DE TRÂNSITO ANIMAL" in texto:
        return "GTA"

    if "FATURA:" in texto:
        return "CONTRA NOTA"

    return "NOTA FISCAL"


def extrair_campos(texto, arquivo):

    tipo = identificar_tipo(texto)

    numero_gta = ""

    gta_match = re.search(
        r"e-GTA[: ]+([A-Z0-9]+)",
        texto,
        re.IGNORECASE
    )

    if gta_match:
        numero_gta = gta_match.group(1)

    if not numero_gta:
        gta_match = re.search(
    
