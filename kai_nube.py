import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Kai - IA Real", layout="wide")
st.title("🌊 Kai - Asistente con IA Real")

# ========== CONFIGURACIÓN ==========
try:
    DEEPSEEK_API_KEY = st.secrets["DEEPSEEK_API_KEY"]
    st.success("✅ API Key cargada desde Secrets")
except Exception as e:
    st.error(f"❌ Error al cargar Secrets: {e}")
    st.stop()

cliente = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com/v1"
)

def responder_con_ia(mensaje, historial):
    messages = [
        {"role": "system", "content": "Eres Kai, un asistente amigable. Hablas de forma natural y cálida. Usas emojis ocasionalmente."}
    ]
    
    for msg in historial[-10:]:
        messages.append({"role": "user", "content": msg["usuario"]})
        messages.append({"role": "assistant", "content": msg["respuesta"]})
    
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
    if st.button("Limpiar conversación"):
        st.session_state.historial = []
        st.rerun()
