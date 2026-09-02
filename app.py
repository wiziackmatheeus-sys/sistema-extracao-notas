import re
from io import BytesIO

import pandas as pd
import pdfplumber
import streamlit as st


st.title("Extrator de Notas de Gado")


def ler(arquivo):
    arquivo.seek(0)
    texto = ""

    with pdfplumber.open(arquivo) as pdf:
        for pagina in pdf.pages:
            conteudo = pagina.extract_text() or ""
            texto += conteudo + " "

    return " ".join(texto.split())


def achar(texto, padrao):
    resultado = re.search(
        padrao,
        texto,
        re.I
    )

    if resultado:
        return resultado.group(1).strip()

    return ""


def valor_total(texto):
    valores = re.findall(
        r"[\d.]+,\d{2}",
        texto
    )

    numeros = []

    for item in valores:
        numero = float(
            item
            .replace(".", "")
            .replace(",", ".")
        )

        if numero > 100:
            numeros.append(numero)

    if not numeros:
        return ""

    saida = f"{max(numeros):,.2f}"

    return (
        saida
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def extrair(arquivo):
    texto = ler(arquivo)
    alto = texto.upper()

    if "E-GTA" in alto:
        tipo = "GTA"

    elif "FATURA:" in alto:
        tipo = "CONTRA NOTA"

    else:
        tipo = "NOTA FISCAL"

    nome = achar(
        texto,
        r"RECEBEMOS DE (.*?) OS PRODUTOS"
    )

    if tipo == "GTA":
        nome = achar(
            texto,
            (
                r"Procedência.*?Nome: "
                r"(.*?) Estabelecimento:"
            )
        )

    gta = achar(
        texto,
        (
            r"GTA:?\s*"
            r"([A-Z]{0,2}\d+[A-Z]?)"
        )
    )

    data = achar(
        texto,
        (
            r"Emissão em: "
            r"(\d{2}/\d{2}/\d{4})"
        )
    )

    if not data:
        data = achar(
            texto,
            (
                r"DATA DA EMISSÃO.*?"
                r"(\d{2}/\d{2}/\d{4})"
            )
        )

    if not data:
        data = achar(
            texto,
            (
                r"DATA DA EMISSÃO.*?"
                r"(\d{2}/\d{2}/\d{2})"
            )
        )

    nota = ""
    contra = ""

    if tipo == "CONTRA NOTA":
        contra = achar(
            texto,
            r"Fatura: (\d+)"
        )

        nota = achar(
            texto,
            (
                r"Contribuinte: NF "
                r"([\d.]+)"
            )
        )

    elif tipo == "NOTA FISCAL":
        nota = achar(
            texto,
            (
                r"NF-e Nº:.*?"
                r"(\d{3}\.\d{3}\.\d{3})"
            )
        )

    if tipo == "GTA":
        valor = ""
    else:
        valor = valor_total(texto)

    return {
        "Arquivo": arquivo.name,
        "Tipo": tipo,
        "Pecuarista": nome,
        "Número da Nota": nota,
        "Número da Contra Nota": contra,
        "Número da GTA": gta,
        "Data de Emissão": data,
        "Valor": valor
    }


def excel(tabela):
    memoria = BytesIO()

    with pd.ExcelWriter(
        memoria,
        engine="openpyxl"
    ) as writer:
        tabela.to_excel(
            writer,
            index=False
        )

    return memoria.getvalue()


arquivos = st.file_uploader(
    "Selecione os PDFs",
    type=["pdf"],
    accept_multiple_files=True
)


if arquivos:
    st.success(
        f"{len(arquivos)} PDF(s) carregado(s)"
    )

    if st.button("Processar"):
        registros = []

        for arquivo in arquivos:
            try:
                registros.append(
                    extrair(arquivo)
                )

            except Exception as erro:
                registros.append(
                    {
                        "Arquivo": arquivo.name,
                        "Tipo": "ERRO",
                        "Pecuarista": "",
                        "Número da Nota": "",
                        "Número da Contra Nota": "",
                        "Número da GTA": "",
                        "Data de Emissão": "",
                        "Valor": str(erro)
                    }
                )

        tabela = pd.DataFrame(
            registros
        )

        st.subheader("Resultado")

        st.dataframe(
            tabela,
            use_container_width=True
        )

        st.download_button(
            label="Baixar Excel",
            data=excel(tabela),
            file_name="historico_notas.xlsx"
        )

else:
    st.info(
        "Adicione os PDFs para começar."
    )
