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


def identificar_tipo(texto):

    texto_maiusculo = texto.upper()

    if "E-GTA" in texto_maiusculo or "GUIA DE TRÂNSITO ANIMAL" in texto_maiusculo:
        return "GTA"

    if "FATURA:" in texto_maiusculo:
        return "CONTRA NOTA"

   
