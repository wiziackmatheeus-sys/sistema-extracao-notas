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
                pagina_texto = pagina.extract_text()

                if pagina_texto:
                    texto += pagina_texto + "\n"

    except Exception:
        pass

    return texto


def localizar(padroes, texto):

    for padrao in padroes:

        resultado = re.search(
            padrao,
            texto,
            re.IGNORECASE | re.DOTALL
        )

        if resultado:
            return resultado.group(1).strip()

    return ""


def identificar_documento(texto):

    texto_maiusculo = texto.upper()

    if "GUIA DE TRÂNSITO ANIMAL" in texto_maiusculo or "E-GTA" in texto_maiusculo:
        return "GTA"

    if "FATURA:" in texto_maiusculo:
        return "CONTRA NOTA"

    return "NF"


def extrair_campos(texto, nome_arquivo):

    tipo = identificar_documento(texto)

    pecuarista = localizar(
        [
            r"NOME:\s*([A-ZÀ-Ú\s]+)",
            r"NOME \/ RAZÃO SOCIAL\s*\**\s*([A-ZÀ-Ú\s]+)",
            r"EMITENTE.*?([A-ZÀ-Ú\s]{5,})"
        ],
        texto
    )

    data_emissao = localizar(
        [
            r"EMISSÃO EM:\s*(\d{2}/\d{2}/\d{4})",
            r"DATA DA EMISSÃO\s*\**\s*(\d{2}/\d{2}/\d{4})",
            r"(\d{2}/\d{2}/\d{4})"
        ],
        texto
    )

    numero_gta = localizar(
        [
            r"e-GTA:\*\*\s*([A-Z0-9]+)",
            r"GTA:\s*([A-Z0-9]+)"
        ],
        texto
    )

    numero_nf = localizar(
        [
            r"NF-e Nº:.*?(\d{3}\.\d{3}\.\d{3})",
            r"NF\s+(\d+)"
        ],
        texto
    )

    numero_contranota = localizar(
        [
            r"Fatura:\s*(\d+)",
            r"No:\s*000\.(\d+)"
        ],
        texto
    )

    valor = localizar(
        [
            r"VALOR TOTAL DA NOTA\s*([\d\.,]+)",
            r"VALOR TOTAL:\s*R\$\s*([\d\.,]+)",
            r"VALOR LÍQUIDO:\s*([\d\.,]+)"
        ],
        texto
    )

    return {
        "Arquivo": nome_arquivo,
        "Tipo": tipo,
        "Pecuarista": pecuarista,
        "Numero NF": numero_nf,
        "Numero Contra Nota": numero_contranota,
        "Numero GTA": numero_gta,
        "Data Emissao": data_emissao,
        "Valor": valor
    }


arquivos = st.file_uploader(
    "Selecione os PDFs",
    type=["pdf"],
    accept_multiple_files=True
)

if arquivos:

    registros = []

    progresso = st.progress(0)

    total = len(arquivos)

    for i, arquivo in enumerate(arquivos):

        texto = ler_pdf(arquivo)

        dados = extrair_campos(
            texto,
            arquivo.name
        )
