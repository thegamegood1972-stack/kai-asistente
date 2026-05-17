import streamlit as st
import requests

st.set_page_config(page_title="Kai - Buscador", layout="wide")

st.title("🌊 Kai - Buscador de Información")
st.markdown("Búscame cualquier tema: *redes neuronales*, *inteligencia artificial*, etc.")

def buscar(tema):
    tema = tema.lower().strip()
    
    # Corregir errores comunes
    if "redes neurales" in tema or "redes neuronal" in tema:
        tema = "red neuronal artificial"
    if tema == "redes neuronales":
        tema = "red neuronal artificial"
    
    if len(tema) < 3:
        return "¿Qué quieres buscar? Por ejemplo: 'redes neuronales'"
    
    try:
        url = f"https://es.wikipedia.org/api/rest_v1/page/summary/{tema.replace(' ', '_')}"
        r = requests.get(url, headers={"User-Agent": "KaiBot"})
        if r.status_code == 200:
            data = r.json()
            titulo = data.get("title", tema)
            texto = data.get("extract", "")[:600]
            return f"**{titulo}**\n\n{texto}\n\n📚 Fuente: Wikipedia"
        else:
            return f"No encontré información sobre '{tema}'. Prueba con 'redes neuronales'."
    except:
        return "Error de conexión. Intenta de nuevo."

if 'historial' not in st.session_state:
    st.session_state.historial = []

for msg in st.session_state.historial[-20:]:
    st.markdown(f"**👤 Tú:** {msg['usuario']}")
    st.markdown(f"**🌊 Kai:** {msg['respuesta']}")
    st.markdown("---")

prompt = st.text_input("Escribe tu búsqueda:", placeholder="Ej: redes neuronales, inteligencia artificial")

if st.button("Buscar") and prompt:
    respuesta = buscar(prompt)
    st.session_state.historial.append({"usuario": prompt, "respuesta": respuesta})
    st.rerun()
