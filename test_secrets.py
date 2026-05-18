import streamlit as st

st.set_page_config(page_title="Test de Secrets", layout="centered")
st.title("🔧 Probando Secrets de Streamlit")

# 1. Primero, listamos TODAS las claves que Streamlit Cloud puede ver
st.write("### 1. Claves encontradas en `st.secrets`:")

if st.secrets:
    for key in st.secrets.keys():
        # Mostramos el nombre de la clave, pero no el valor por seguridad
        st.write(f"- Clave encontrada: **{key}**")
else:
    st.error("No se encontró ninguna clave en `st.secrets`.")

st.divider()

# 2. Luego, intentamos leer la clave específica que necesitas
st.write("### 2. Buscando la clave `GEMINI_API_KEY`:")

if "GEMINI_API_KEY" in st.secrets:
    # Si la encuentra, muestra un mensaje de éxito
    st.success("✅ ¡SÍ se encontró la clave `GEMINI_API_KEY` en Secrets!")
    st.info("La clave se ha cargado correctamente. El problema está en otra parte.")
else:
    # Si NO la encuentra, intentamos buscar una alternativa
    st.error("❌ No se encontró la clave `GEMINI_API_KEY`. Revisa la configuración.")
    st.write("**Posibles soluciones:**")
    st.write("1. Ve a **Settings > Secrets** de tu app en Streamlit Cloud.")
    st.write("2. Asegúrate de que la línea esté escrita EXACTAMENTE así:")
    st.code('GEMINI_API_KEY = "AIzaSyA61W-BDqDh4JOgk1a3ZEdbBkCMqQaoaLA"', language="toml")
    st.write("3. **Borra cualquier línea adicional** que pueda haber en el archivo.")
    st.write("4. Haz clic en **Save** y luego en **Reboot** (··· > Reboot).")
    st.stop()
