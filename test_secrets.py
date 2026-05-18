import streamlit as st

st.set_page_config(page_title="Test de Secrets", layout="centered")
st.title("🔧 Probando Secrets de Streamlit")

st.write("### Claves encontradas en `st.secrets`:")

if st.secrets:
    for key in st.secrets.keys():
        st.write(f"- Clave encontrada: **{key}**")
else:
    st.error("No se encontró ninguna clave en `st.secrets`.")

st.divider()

if "GEMINI_API_KEY" in st.secrets:
    st.success("✅ ¡SÍ se encontró la clave `GEMINI_API_KEY` en Secrets!")
else:
    st.error("❌ No se encontró la clave `GEMINI_API_KEY`.")
    st.code('GEMINI_API_KEY = "tu-clave-real"', language="toml")