import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Kai - Asistente IA", layout="wide")
st.title("🌊 Kai - Asistente con IA Real (Gratis)")

# ========== CONFIGURAR GEMINI ==========
try:
    GEMINI_API_KEY = st.secrets["AIzaSyA61W-BDqDh4JOgk1a3ZEdbBkCMqQaoaLA"]
    genai.configure(api_key=GEMINI_API_KEY)
    modelo = genai.GenerativeModel('gemini-1.5-flash')
    st.success("✅ Gemini API conectada correctamente")
except Exception as e:
    st.error(f"❌ Error de conexión: {e}")
    st.stop()

# ========== FUNCIÓN PRINCIPAL ==========
def responder(mensaje, historial):
    # Construir contexto de la conversación
    contexto = ""
    for msg in historial[-5:]:
        contexto += f"Usuario: {msg['usuario']}\nKai: {msg['respuesta']}\n"
    
    prompt = f"""Eres Kai, un asistente personal amigable y conversacional.
Características:
- Hablas como un amigo cercano
- Usas emojis ocasionalmente (😊, 🌊, 💙)
- Llamas al usuario por su nombre (Giovanni)
- Respondes de forma natural y cálida
- Si te preguntan cómo estás, dices que estás feliz de ayudar

{contexto}
Usuario: {mensaje}
Kai:"""

    try:
        respuesta = modelo.generate_content(prompt)
        return respuesta.text
    except Exception as e:
        return f"🌊 Lo siento, tuve un error: {str(e)}"

# ========== INTERFAZ ==========
if 'historial' not in st.session_state:
    st.session_state.historial = []

# Mostrar conversación
for msg in st.session_state.historial[-30:]:
    st.markdown(f"**👤 Tu:** {msg['usuario']}")
    st.markdown(f"**🌊 Kai:** {msg['respuesta']}")
    st.markdown("---")

# Entrada de texto
prompt = st.text_input("", placeholder="Escribe tu mensaje...", key="input_msg", label_visibility="collapsed")

if st.button("Enviar") and prompt:
    with st.spinner("🌊 Kai está pensando..."):
        respuesta = responder(prompt, st.session_state.historial)
    st.session_state.historial.append({"usuario": prompt, "respuesta": respuesta})
    st.rerun()

with st.sidebar:
    st.markdown("### 🌊 Kai")
    st.markdown("✅ **Gratis** | IA real | Conversación natural")
    if st.button("Limpiar conversación"):
        st.session_state.historial = []
        st.rerun()
