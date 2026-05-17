import streamlit as st

st.set_page_config(page_title="Prueba de Secrets", layout="wide")
st.title("🔧 Diagnóstico de Secrets")

# Mostrar todas las claves disponibles en Secrets
st.write("### Claves disponibles en Secrets:")

try:
    # Intentar listar todas las claves
    todas_las_claves = list(st.secrets.keys())
    st.write(f"Claves encontradas: {todas_las_claves}")
    
    if "GEMINI_API_KEY" in st.secrets:
        st.success("✅ GEMINI_API_KEY ENCONTRADA en Secrets")
        # Mostrar solo los primeros caracteres por seguridad
        clave = st.secrets["GEMINI_API_KEY"]
        st.write(f"La clave comienza con: {clave[:15]}...")
    else:
        st.error("❌ GEMINI_API_KEY NO encontrada en Secrets")
        st.write("Las claves disponibles son:", todas_las_claves)

except Exception as e:
    st.error(f"Error al leer Secrets: {e}")

st.markdown("---")
st.markdown("### Solucion:")
st.markdown("1. Ve a https://share.streamlit.io")
st.markdown("2. Entra a tu app")
st.markdown("3. Haz clic en Settings (tres puntos -> Settings)")
st.markdown("4. Ve a la pestaña Secrets")
st.markdown("5. Agrega exactamente:")
st.code('GEMINI_API_KEY = "tu-clave-real-de-gemini"', language="toml")
st.markdown("6. Haz clic en Save")
st.markdown("7. Reinicia la app (tres puntos -> Reboot)")
