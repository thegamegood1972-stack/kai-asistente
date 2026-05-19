import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Kai - Asistente", layout="wide")
st.title("🌊 Kai - Asistente con IA")

# Configuración de Gemini
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
    st.success("✅ Conectado a Gemini")
except Exception as e:
    st.error(f"Error de conexión: {e}")
    st.stop()

# Interfaz de chat
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Escribe tu mensaje aquí..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            response = model.generate_content(prompt)
            st.markdown(response.text)
    st.session_state.messages.append({"role": "assistant", "content": response.text})
