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
st.markdown("### Solución:")
st.markdown("""
1. Ve a https://share.streamlit.io
2. Entra a tu app
3. Haz clic en **Settings** (tres puntos → Settings)
4. Ve a la pestaña **Secrets**
5. Agrega exactamente:

```toml
GEMINI_API_KEY = "AIzaSyA61W-BDqDh4JOgk1a3ZEdbBkCMqQaoaLA"
