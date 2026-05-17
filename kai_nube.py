import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Kai - IA Real", layout="wide")
st.title("🌊 Kai - Asistente con IA Real (Gratis)")

# Configurar Gemini
try:
    GEMINI_API_KEY = st.secrets["AIzaSyA61W-BDqDh4JOgk1a3ZEdbBkCMqQaoaLA"]
    genai.configure(api_key=GEMINI_API_KEY)
    modelo = genai.GenerativeModel('gemini-1.5-flash')
    st.success("✅ Gemini API conectada (Completamente Gratis)")
except:
    st.error("❌ No se encontró GEMINI_API_KEY en Secrets")
    st.stop()

def responder_con_ia(mensaje, historial):
    # Construir contexto
    contexto = ""
    for msg in historial[-5:]:
        contexto += f"Usuario: {msg['usuario']}\nKai: {msg['respuesta']}\n"
    
    prompt = f"""Eres Kai, un asistente amigable y conversacional.
Hablas como un amigo, usas emojis ocasionalmente.
Llamas al usuario por su nombre si lo sabes.

{contexto}
Usuario: {mensaje}
Kai:"""

    try:
        respuesta = modelo.generate_content(prompt)
        return respuesta.text
    except Exception as e:
        return f"🌊 Error: {str(e)}"

# ========== INTERFAZ ==========
if 'historial' not in st.session_state:
    st.session_state.historial = []

for msg in st.session_state.historial[-30:]:
    st.markdown(f"**👤 Tu:** {msg['usuario']}")
    st.markdown(f"**🌊 Kai:** {msg['respuesta']}")
    st.markdown("---")

prompt = st.text_input("", placeholder="Ej: Hola Kai, ¿cómo estás?", key="input_msg", label_visibility="collapsed")

if st.button("Enviar") and prompt:
    with st.spinner("🌊 Kai está pensando..."):
        respuesta = responder_con_ia(prompt, st.session_state.historial)
    st.session_state.historial.append({"usuario": prompt, "respuesta": respuesta})
    st.rerun()

with st.sidebar:
    st.markdown("### 🌊 Kai")
    st.markdown("✅ **Gratis** | Sin tarjeta | Sin límites")
    if st.button("Limpiar conversación"):
        st.session_state.historial = []
        st.rerun()
