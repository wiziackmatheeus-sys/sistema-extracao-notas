import streamlit as st

st.set_page_config(
    page_title="Extrator de Notas de Gado",
    layout="wide"
)

st.title("🐂 Extrator de Notas de Gado")

arquivos = st.file_uploader(
    "Selecione os PDFs",
    type=["pdf"],
    accept_multiple_files=True
)

if arquivos:
    st.success(f"{len(arquivos)} arquivo(s) carregado(s)")
``
