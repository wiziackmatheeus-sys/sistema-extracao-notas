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


def extrair_info(texto, nome_arquivo):

    tipo = "NF"

    if "GUIA DE TRÂNSITO ANIMAL" in texto.upper() or "E-GTA" in texto.upper():
        tipo = "GTA"

    elif "FATURA:" in texto.upper():
        tipo = "CONTRA NOTA"

    numero_gta = ""

    match = re.search(r"PA[0-9A-Z]+", texto)

    if match:
        numero_gta = match.group(0)

    data = ""

    match = re.search(r"(\d{2}/\d{2}/\d{4})", texto)

    if match:
        data = match.group(1)

    valor = ""

    match = re.search(
        r"VALOR TOTAL DA NOTA.*?([\d\.]+,\d{2})",
        texto,
        re.IGNORECASE
    )

    if match:
        valor = match.group(1)

    if not valor:

        match = re.search(
            r"VALOR TOTAL:\s*R\$\s*([\d\.]+,\d{2})",
            texto,
            re.IGNORECASE
        )

        if match:
            valor = match.group(1)

    nota = ""

    match = re.search(
        r"004\.([0-9\.]+)",
        texto
    )

    if match:
        nota = match.group(1)

    contranota = ""

    match = re.search(
        r"Fatura:\s*(\d+)",
        texto,
        re.IGNORECASE
    )

    if match:
        contranota = match.group(1)

    pecuarista = ""

    match = re.search(
        r"ADALBERTO TADEU DE ALMEIDA",
        texto,
        re.IGNORECASE
    )

    if match:
        pecuarista = match.group(0)

    return {
        "Arquivo": nome_arquivo,
        "Tipo": tipo,
        "Pecuarista": pecuarista,
        "Numero Nota": nota,
        "Numero Contra Nota": contranota,
        "Numero GTA": numero_gta,
        "Data": data,
        "Valor": valor
    }


arquivos = st.file_uploader(
    "Selecione os PDFs",
