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
st.caption("Envie GTA, Nota Fiscal e Contra Nota em PDF.")


def ler_pdf(arquivo):
    texto = ""

    arquivo.seek(0)

    with pdfplumber.open(arquivo) as pdf:
        for pagina in pdf.pages:
            conteudo = pagina.extract_text() or ""
            texto += conteudo + "\n"

    return " ".join(texto.split())


def primeiro_resultado(texto, padroes):
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
    pecuarista = ""

    if tipo == "GTA":
        pecuarista = primeiro_resultado(
            texto,
            [
                (
                    r"Procedência.*?Nome:\s*([^*]+?)"
                    r"(?=\s+Estabelecimento:)"
                )
            ]
        )

    elif tipo == "CONTRA NOTA":
        pecuarista = primeiro_resultado(
            texto,
            [
                (
                    r"DESTINATÁRIO\s*/\s*REMETENTE.*?"
                    r"NOME\s*/\s*RAZÃO SOCIAL\s*\**\s*"
                    r"([A-ZÀ-Ú0-9 .,&'-]+?)"
                    r"(?=\s+CNPJ\s*/\s*CPF)"
                ),
                (
                    r"RECEBEMOS DE\s+(.+?)"
                    r"(?=\s+-\s+OTR|\s+OS PRODUTOS)"
                )
            ]
        )

    else:
        pecuarista = primeiro_resultado(
            texto,
            [
                (
                    r"EMITENTE.*?"
                    r"NOME\s*/\s*NOME EMPRESARIAL.*?"
                    r"HORA DA SAÍDA\s+"
                    r"([A-ZÀ-Ú0-9 .,&'-]+?)\s+"
                    r"\d{3}[.]?\d{3}[.]?\d{3}[-/]?\d{2}"
                ),
                (
                    r"RECEBEMOS DE\s+(.+?)"
                    r"(?=\s+OS PRODUTOS)"
                )
            ]
        )

    return pecuarista


def extrair_dados(texto, nome_arquivo):
    tipo = identificar_tipo(texto)

    pecuarista = extrair_pecuarista(
        texto,
        tipo
    )

    numero_gta = primeiro_resultado(
        texto,
        [
            r"e-GTA:\s*([A-Z]{0,2}\d+[A-Z]?)",
            r"GTA:\s*([A-Z]{0,2}\d+[A-Z]?)"
        ]
    )

    data_emissao = primeiro_resultado(
        texto,
        [
            r"Emissão em:\s*(\d{2}/\d{2}/\d{4})",
            r"DATA DA EMISSÃO\s*(\d{2}/\d{2}/\d{4})",
            (
                r"DATA DA EMISSÃO.*?"
                r"(\d{2}/\d{2}/\d{2})(?:\s|$)"
            )
        ]
    )

    numero_nota = ""
    numero_contra_nota = ""

    if tipo == "NOTA FISCAL":
        numero_nota = primeiro_resultado(
            texto,
            [
                r"NF-e Nº:.*?(\d{3}[.]\d{3}[.]\d{3})",
                r"Nº:\s*(\d{3}[.]\d{3}[.]\d{3})"
            ]
        )

    elif tipo == "CONTRA NOTA":
        numero_contra_nota = primeiro_resultado(
            texto,
            [
                r"Fatura:\s*(\d+)",
                r"NF-e No[.]?\s*0*(\d+)"
            ]
        )

        numero_nota = primeiro_resultado(
            texto,
            [
                r"Inf[.] Contribuinte:\s*NF\s*([\d.]+)"
            ]
        )

    valor = primeiro_resultado(
        texto,
        [
            (
                r"VALOR TOTAL DA NOTA\s*"
                r"([\d.]+,\d{2})"
            ),
            (
                r"VALOR TOTAL:\s*R[$]\s*"
                r"([\d.]+,\d{2})"
            ),
            (
                r"Valor Líquido:\s*"
                r"([\d.]+(?:,\d{2})?)"
            )
        ]
    )

    pendencias = []

    if not pecuarista:
        pendencias.append("pecuarista")

    if tipo == "GTA" and not numero_gta:
        pendencias.append("GTA")

    if tipo == "NOTA FISCAL" and not numero_nota:
        pendencias.append("nota")

    if tipo == "CONTRA NOTA" and not numero_contra_nota:
        pendencias.append("contra nota")

    if tipo != "GTA"
