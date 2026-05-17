import streamlit as st
import requests

st.set_page_config(page_title="Kai - Asistente IA", layout="wide")
st.title("🌊 Kai - Asistente de IA")

def dar_formula_snl():
    return "**Sistemas No Lineales**\n\nNo existe una formula unica. Ejemplo:\n```\ndx/dt = x^2 - 1\ndy/dt = x*y + y\n```"

def dar_codigo_saludo():
    return "**Python - Saludo**\n```python\nnombre = input('¿Como te llamas? ')\nprint(f'¡Hola {nombre}!')\n```"

def buscar_wikipedia(tema):
    try:
        url = f"https://es.wikipedia.org/api/rest_v1/page/summary/{tema.replace(' ', '_')}"
        r = requests.get(url, headers={"User-Agent": "KaiBot"})
        if r.status_code == 200:
            data = r.json()
            return f"**{data.get('title', tema)}**\n\n{data.get('extract', '')[:500]}\n\n📚 Wikipedia"
        return f"No encontre '{tema}'"
    except:
        return "Error de conexion"

def responder(mensaje):
    m = mensaje.lower()
    
    if "hola" in m:
        return "🌊 ¡Hola! ¿Que quieres saber?"
    
    if "formula" in m and "sistema no lineal" in m:
        return dar_formula_snl()
    
    if "codigo" in m and "saludo" in m:
        return dar_codigo_saludo()
    
    if "inteligencia artificial" in m:
        return buscar_wikipedia("inteligencia artificial")
    
    if "redes neuronales" in m or "redes neurales" in m:
        return buscar_wikipedia("red neuronal artificial")
    
    return buscar_wikipedia(m)

if 'historial' not in st.session_state:
    st.session_state.historial = []

for msg in st.session_state.historial[-30:]:
    st.markdown(f"**👤 Tu:** {msg['usuario']}")
    st.markdown(f"**🌊 Kai:** {msg['respuesta']}")
    st.markdown("---")

prompt = st.text_input("", placeholder="Ej: formula de sistema no lineal", key="input_msg", label_visibility="collapsed")

if st.button("Enviar") and prompt:
    respuesta = responder(prompt)
    st.session_state.historial.append({"usuario": prompt, "respuesta": respuesta})
    st.rerun()

with st.sidebar:
    st.markdown("### 🌊 Kai")
    st.markdown("- formula de sistema no lineal")
    st.markdown("- inteligencia artificial")
    st.markdown("- redes neuronales")
    st.markdown("- codigo de saludo")
    if st.button("Limpiar"):
        st.session_state.historial = []
        st.rerun()
