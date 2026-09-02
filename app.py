import streamlit as st
import pdfplumber
import pandas as pd
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


arquivos = st.file_uploader(
    "Selecione os PDFs",
    type=["pdf"],
    accept_multiple_files=True
)

if arquivos:

    dados = []

    for arquivo in arquivos:

        texto = ler_pdf(arquivo)

        st.subheader(arquivo.name)

        st.write("Caracteres encontrados:", len(texto))

        with st.expander("Ver texto extraído"):
            st.text(texto[:5000])

        dados.append({
            "Arquivo": arquivo.name,
            "Caracteres": len(texto)
        })

    df = pd.DataFrame(dados)

    st.subheader("Resumo")

    st.dataframe(df, use_container_width=True)

    excel = BytesIO()

    with pd.ExcelWriter(
        excel,
        engine="openpyxl"
    ) as writer:

        df.to_excel(
            writer,
            sheet_name="Resumo",
            index=False
        )

    st.download_button(
        "📥 Baixar Excel",
        data=excel.getvalue(),
        file_name="resultado.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
