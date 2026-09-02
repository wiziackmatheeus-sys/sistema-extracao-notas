import re
from io import BytesIO

import pandas as pd
import pdfplumber
import streamlit as st

st.set_page_config(page_title="Extrator de Notas de Gado", layout="wide")
st.title("🐂 Extrator de Notas de Gado")
st.write("Envie GTA, Nota Fiscal e Contra Nota em PDF.")


def ler_pdf(arquivo):
    texto = ""
    arquivo.seek(0)
    with pdfplumber.open(arquivo) as pdf:
        for pagina in pdf.pages:
            texto += (pagina.extract_text() or "") + "\n"
    return " ".join(texto.split())


def procurar(texto, padroes):
    for padrao in padroes:
        resultado = re.search(padrao, texto, re.IGNORECASE)
        if resultado:
            return resultado.group(1).strip(" .,-")
    return ""


def identificar_tipo(texto):
    maiusculo = texto.upper()
    if "GUIA DE TRÂNSITO ANIMAL" in maiusculo or "E-GTA" in maiusculo:
        return "GTA"
    if "FATURA:" in maiusculo or "ENT MERC REC C/FIM ESP" in maiusculo:
        return "CONTRA NOTA"
    return "NOTA FISCAL"


def extrair_dados(texto, nome_arquivo):
    tipo = identificar_tipo(texto)

    if tipo == "GTA":
        pecuarista = procurar(texto, [
            r"Procedência.*?Nome:\s*(.+?)\s+Estabelecimento:"
        ])
    elif tipo == "CONTRA NOTA":
        pecuarista = procurar(texto, [
            r"DESTINATÁRIO\s*/\s*REMETENTE.*?NOME\s*/\s*RAZÃO SOCIAL\s*\**\s*(.+?)\s+CNPJ\s*/\s*CPF",
            r"RECEBEMOS DE\s+(.+?)(?:\s+-\s+OTR|\s+OS PRODUTOS)"
        ])
    else:
        pecuarista = procurar(texto, [
            r"RECEBEMOS DE\s+(.+?)\s+OS PRODUTOS",
            r"HORA DA SAÍDA\s+(.+?)\s+\d{3}[.]?\d{3}[.]?\d{3}[-/]?\d{2}"
        ])

    numero_gta = procurar(texto, [
        r"e-GTA:\s*([A-Z]{0,2}\d+[A-Z]?)",
        r"GTA:\s*([A-Z]{0,2}\d+[A-Z]?)"
    ])

    data_emissao = procurar(texto, [
        r"Emissão em:\s*(\d{2}/\d{2}/\d{4})",
        r"DATA DA EMISSÃO\s*(\d{2}/\d{2}/\d{4})",
        r"DATA DA EMISSÃO.*?(\d{2}/\d{2}/\d{2})"
    ])

    numero_nota = ""
    numero_contra_nota = ""

    if tipo == "NOTA FISCAL":
        numero_nota = procurar(texto, [
            r"NF-e Nº:.*?(\d{3}[.]\d{3}[.]\d{3})",
            r"Nº:\s*(\d{3}[.]\d{3}[.]\d{3})"
        ])

    if tipo == "CONTRA NOTA":
        numero_contra_nota = procurar(texto, [
            r"Fatura:\s*(\d+)",
            r"NF-e No[.]?\s*0*(\d+)"
        ])
        numero_nota = procurar(texto, [
            r"Inf[.] Contribuinte:\s*NF\s*([\d.]+)"
        ])

    valor = procurar(texto, [
        r"VALOR TOTAL DA NOTA\s*([\d.]+,\d{2})",
        r"VALOR TOTAL:\s*R[$]\s*([\d.]+,\d{2})",
        r"Valor Líquido:\s*([\d.]+(?:,\d{2})?)"
    ])

    pendencias = []
    if not pecuarista:
        pendencias.append("pecuarista")
    if tipo == "GTA" and not numero_gta:
        pendencias.append("GTA")
    if tipo == "NOTA FISCAL" and not numero_nota:
        pendencias.append("nota")
    if tipo == "CONTRA NOTA" and not numero_contra_nota:
        pendencias.append("contra nota")
    if tipo != "GTA" and not valor:
        pendencias.append("valor")

    status = "OK" if not pendencias else "Revisar: " + ", ".join(pendencias)

    return {
        "Arquivo": nome_arquivo,
        "Tipo": tipo,
        "Pecuarista": pecuarista,
        "Número da Nota": numero_nota,
        "Número da Contra Nota": numero_contra_nota,
        "Número da GTA": numero_gta,
        "Data de Emissão": data_emissao,
        "Valor": valor,
        "Status": status,
    }


def criar_excel(df):
    saida = BytesIO()
    with pd.ExcelWriter(saida, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Documentos")
    saida.seek(0)
    return saida.getvalue()


arquivos = st.file_uploader(
    "Selecione os PDFs",
    type=["pdf"],
    accept_multiple_files=True,
)

if arquivos:
    st.success(f"{len(arquivos)} PDF(s) carregado(s)")

    if st.button("Processar documentos", type="primary"):
        registros = []
        barra = st.progress(0)

        for indice, arquivo in enumerate(arquivos):
            try:
                texto = ler_pdf(arquivo)
                registros.append(extrair_dados(texto, arquivo.name))
            except Exception as erro:
                registros.append({
                    "Arquivo": arquivo.name,
                    "Tipo": "",
                    "Pecuarista": "",
                    "Número da Nota": "",
                    "Número da Contra Nota": "",
                    "Número da GTA": "",
                    "Data de Emissão": "",
                    "Valor": "",
                    "Status": f"Erro: {erro}",
                })

            barra.progress((indice + 1) / len(arquivos))

        df = pd.DataFrame(registros)
        st.subheader("Resultado")
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.download_button(
            label="Baixar Excel",
            data=criar_excel(df),
            file_name="historico_notas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
else:
    st.info("Adicione os PDFs para começar.")
