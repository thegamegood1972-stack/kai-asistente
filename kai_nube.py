import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Kai - Asistente IA", layout="wide")
st.title("🌊 Kai - Asistente con IA Real (Gratis)")

# ========== CONFIGURAR GEMINI ==========
try:
    # Esta línea lee la clave desde Secrets - NO LA CAMBIES
    GEMINI_API_KEY = st.secrets["AIzaSyA61W-BDqDh4JOgk1a3ZEdbBkCMqQaoaLA"]
    genai.configure(api_key=GEMINI_API_KEY)
    modelo = genai.GenerativeModel('gemini-1.5-flash')
    st.success("✅ Gemini API conectada correctamente")
except Exception as e:
    st.error(f"❌ Error: {e}")
    st.stop()

def responder(mensaje, historial):
    contexto = ""
    for msg in historial[-5:]:
        contexto += f"Usuario: {msg['usuario']}\nKai: {msg['respuesta']}\n"
    
    prompt = f"""Eres Kai, un asistente amigable. Hablas como un amigo.

{contexto}
Usuario: {mensaje}
Kai:"""

    try:
        respuesta = modelo.generate_content(prompt)
        return respuesta.text
    except Exception as e:
        return f"🌊 Error: {str(e)}"

if 'historial' not in st.session_state:
    st.session_state.historial = []

for msg in st.session_state.historial[-30:]:
    st.markdown(f"**👤 Tu:** {msg['usuario']}")
    st.markdown(f"**🌊 Kai:** {msg['respuesta']}")
    st.markdown("---")

prompt = st.text_input("", placeholder="Escribe tu mensaje...", key="input_msg", label_visibility="collapsed")

if st.button("Enviar") and prompt:
    with st.spinner("🌊 Kai está pensando..."):
        respuesta = responder(prompt, st.session_state.historial)
    st.session_state.historial.append({"usuario": prompt, "respuesta": respuesta})
    st.rerun()

with st.sidebar:
    st.markdown("### 🌊 Kai")
    if st.button("Limpiar conversación"):
        st.session_state.historial = []
        st.rerun()
