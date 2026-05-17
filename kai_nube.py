import streamlit as st
import requests
from openai import OpenAI

st.set_page_config(page_title="Kai - IA Real", layout="wide")
st.title("🌊 Kai - Asistente con IA Real")

# ========== CONFIGURACIÓN DEEPSEEK ==========
DEEPSEEK_API_KEY = "sk-aqui-tu-api-key-de-deepseek"  # <--- PON AQUÍ TU API KEY

cliente = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com/v1"
)

# ========== FUNCIÓN PRINCIPAL CON IA ==========
def responder_con_ia(mensaje, historial):
    """Usa DeepSeek para responder de forma inteligente"""
    
    # Construir historial para la IA
    messages = [
        {"role": "system", "content": """Eres Kai, un asistente personal amigable y conversacional.
Características:
- Hablas como un amigo cercano, no como robot
- Respondes de forma natural, cálida y breve
- Llamas al usuario por su nombre (Giovanni)
- Si no sabes algo, lo dices honestamente
- Te interesa cómo se siente el usuario
- Usas emojis ocasionalmente (😊, 🌊, 💙)"""}
    ]
    
    # Agregar historial reciente
    for msg in historial[-10:]:
        messages.append({"role": "user", "content": msg["usuario"]})
        messages.append({"role": "assistant", "content": msg["respuesta"]})
    
    # Agregar mensaje actual
    messages.append({"role": "user", "content": mensaje})
    
    try:
        respuesta = cliente.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0.8,
            max_tokens=300
        )
        return respuesta.choices[0].message.content
    except Exception as e:
        return f"🌊 Lo siento, tengo un problema de conexión: {e}"

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
    st.markdown("**Ahora entiendo conversación normal:**")
    st.markdown("- ¿Cómo estás?")
    st.markdown("- ¿Qué te gusta hacer?")
    st.markdown("- Cuéntame algo interesante")
    st.markdown("- Dame un consejo")
    st.markdown("---")
    if st.button("Limpiar conversación"):
        st.session_state.historial = []
        st.rerun()
    st.markdown("---")
    st.warning("⚠️ **Necesitas API Key de DeepSeek**\n\nVe a platform.deepseek.com y crea una gratis. Ponla en el código donde dice `DEEPSEEK_API_KEY`")
