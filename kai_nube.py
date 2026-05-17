# kai_nube.py - Buscador CORREGIDO
import streamlit as st
import requests
import json
import os
from datetime import datetime

st.set_page_config(page_title="Kai - Buscador", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0a0a2a 0%, #0a0a2a 100%); }
    .user-bubble { background: #0084ff; color: white; padding: 12px 18px; border-radius: 20px; max-width: 80%; margin: 10px 0 10px auto; display: inline-block; }
    .kai-bubble { background: #1a1a3a; color: #00e5ff; padding: 12px 18px; border-radius: 20px; max-width: 85%; margin: 10px auto 10px 0; display: inline-block; border: 1px solid #00e5ff; }
    .message-row { display: flex; width: 100%; margin-bottom: 15px; }
    .user-row { justify-content: flex-end; }
    .kai-row { justify-content: flex-start; }
    .avatar { width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 22px; }
    .kai-avatar { background: #00e5ff; margin-right: 10px; color: #0a0a2a; }
    .user-avatar { background: #0084ff; margin-left: 10px; order: 2; color: white; }
    .hologram-title { text-align: center; font-size: 2rem; font-weight: bold; background: linear-gradient(135deg, #00e5ff, #0077b6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 20px 0; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hologram-title">🌊 KAI - BUSCADOR INTELIGENTE 🌊</div>', unsafe_allow_html=True)

# ========== MEMORIA ==========
MEMORIA_FILE = "memoria_kai.json"

def cargar_memoria():
    if os.path.exists(MEMORIA_FILE):
        with open(MEMORIA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def guardar_memoria(usuario, respuesta):
    memoria = cargar_memoria()
    memoria.append({"fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "usuario": usuario, "respuesta": respuesta})
    with open(MEMORIA_FILE, 'w', encoding='utf-8') as f:
        json.dump(memoria[-100:], f, ensure_ascii=False, indent=2)

# ========== CORRECCIÓN DE ERRORES ORTOGRÁFICOS ==========
def corregir_termino(termino):
    """Corrige errores comunes"""
    t = termino.lower().strip()
    
    correcciones = {
        "redes neurales": "redes neuronales",
        "redes neuronal": "redes neuronales", 
        "neurales": "neuronales",
        "inteligensia": "inteligencia",
        "intelijencia": "inteligencia",
        "artifisial": "artificial",
        "artificiall": "artificial",
        "progrma": "programa",
        "codgio": "codigo"
    }
    
    for incorrecto, correcto in correcciones.items():
        if incorrecto in t:
            return correcto
    return t

# ========== EXTRAER TÉRMINO DE BÚSQUEDA ==========
def extraer_termino(mensaje):
    """Extrae el tema de búsqueda de cualquier frase"""
    m = mensaje.lower().strip()
    
    # Eliminar frases comunes
    eliminar = [
        "buscame", "busca", "encuentrame", "encuentra", "investiga", "quiero saber",
        "tod lo relacionado con", "todo lo relacionado con", "informacion sobre",
        "dame informacion de", "que es", "que son", "definicion de", "explicame"
    ]
    
    for e in eliminar:
        m = m.replace(e, "")
    
    # Limpiar
    m = m.strip().strip("?.,;:! ")
    
    # Corregir errores
    m = corregir_termino(m)
    
    return m

# ========== CÓDIGO PYTHON ==========
def dar_codigo_red_neuronal():
    return """**Código Python - Red Neuronal Simple**

```python
import numpy as np

class RedNeuronal:
    def __init__(self, entradas, salidas):
        self.pesos = np.random.randn(entradas, salidas) * 0.1
    
    def activacion(self, x):
        return 1 / (1 + np.exp(-x))
    
    def predecir(self, entrada):
        return self.activacion(np.dot(entrada, self.pesos))

# Ejemplo
nn = RedNeuronal(2, 1)
print(f"Prediccion: {nn.predecir([0.5, 0.8])}")
```"""

# ========== BÚSQUEDA EN WIKIPEDIA ==========
def buscar_en_wikipedia(termino, usuario):
    """Busca en Wikipedia y devuelve información"""
    
    if not termino or len(termino) < 3:
        return f"🌊 {usuario}, ¿qué quieres buscar? Por ejemplo: 'redes neuronales', 'inteligencia artificial'"
    
    # Casos especiales
    if termino == "redes neuronales":
        termino = "red neuronal artificial"
    
    try:
        # Buscar página exacta
        url = f"https://es.wikipedia.org/api/rest_v1/page/summary/{termino.replace(' ', '_')}"
        response = requests.get(url, headers={"User-Agent": "KaiBot/1.0"})
        
        if response.status_code == 200:
            data = response.json()
            if "extract" in data and data["extract"]:
                titulo = data.get("title", termino)
                extracto = data["extract"][:800]
                return f"🌊 **{titulo}**\n\n{extracto}\n\n📚 Fuente: Wikipedia"
        
        # Búsqueda por coincidencia
        url_buscar = f"https://es.wikipedia.org/w/api.php?action=query&list=search&srsearch={termino}&format=json&origin=*"
        response = requests.get(url_buscar, headers={"User-Agent": "KaiBot/1.0"})
        
        if response.status_code == 200:
            data = response.json()
            resultados = data.get("query", {}).get("search", [])
            if resultados:
                primer = resultados[0]["title"]
                url = f"https://es.wikipedia.org/api/rest_v1/page/summary/{primer.replace(' ', '_')}"
                response = requests.get(url, headers={"User-Agent": "KaiBot/1.0"})
                if response.status_code == 200:
                    data = response.json()
                    if "extract" in data:
                        return f"🌊 **{primer}**\n\n{data['extract'][:800]}\n\n📚 Fuente: Wikipedia"
        
        return f"🌊 {usuario}, no encontré información sobre '{termino}'. ¿Quieres buscar 'redes neuronales' o 'inteligencia artificial'?"
        
    except Exception as e:
        return f"🌊 Error de conexión: {e}. Intenta de nuevo."

# ========== DETECTAR INTENCIÓN ==========
def detectar_intencion(mensaje):
    m = mensaje.lower()
    
    if any(p in m for p in ["codigo", "código", "programa", "script"]):
        return "codigo"
    
    if any(p in m for p in ["hola", "buenos dias", "buenas tardes"]):
        return "saludo"
    
    if any(p in m for p in ["como estas", "cómo estás", "que haces"]):
        return "personal"
    
    if any(p in m for p in ["gracias", "excelente", "perfecto", "genial", "bien"]):
        return "aprobacion"
    
    return "buscar"

# ========== RESPUESTAS ==========
def responder(mensaje, usuario):
    intencion = detectar_intencion(mensaje)
    
    if intencion == "saludo":
        hora = datetime.now().hour
        if hora < 12: saludo = "Buenos días"
        elif hora < 18: saludo = "Buenas tardes"
        else: saludo = "Buenas noches"
        return f"🌊 {saludo} {usuario}! ¿Qué quieres buscar hoy? Puedo encontrar información sobre redes neuronales, inteligencia artificial y más. 🔍"
    
    if intencion == "personal":
        return f"🌊 ¡Estoy muy bien {usuario}! Conectado y listo para buscar lo que necesites. ¿Qué tema te interesa? 🔍"
    
    if intencion == "aprobacion":
        return f"🌊 ¡Me alegra que te sea útil, {usuario}! ¿Necesitas buscar algo más? 🔍"
    
    if intencion == "codigo":
        return dar_codigo_red_neuronal()
    
    # Buscar (intención por defecto)
    termino = extraer_termino(mensaje)
    return buscar_en_wikipedia(termino, usuario)

USUARIO = "Giovanni"

# ========== MOSTRAR CHAT ==========
if 'historial' not in st.session_state:
    st.session_state.historial = cargar_memoria()

if len(st.session_state.historial) == 0:
    bienvenida = f"🌊 ¡Hola {USUARIO}! Soy Kai, tu buscador inteligente.\n\n**Ejemplos:**\n• redes neuronales\n• inteligencia artificial\n• Dame código de red neuronal\n• Hola"
    st.session_state.historial.append({"fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "usuario": "Sistema", "respuesta": bienvenida})

for msg in st.session_state.historial[-30:]:
    if msg['usuario'] != "Sistema":
        st.markdown(f"""
        <div class="message-row user-row">
            <div class="user-bubble">{msg['usuario']}</div>
            <div class="avatar user-avatar">👤</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown(f"""
    <div class="message-row kai-row">
        <div class="avatar kai-avatar">🌊</div>
        <div class="kai-bubble">{msg['respuesta']}</div>
    </div>
    """, unsafe_allow_html=True)

# ========== ENTRADA ==========
col1, col2 = st.columns([4, 1])

with col1:
    prompt = st.text_input("", placeholder="Ej: redes neuronales / inteligencia artificial / dame código / hola", key="input_msg", label_visibility="collapsed")

with col2:
    enviar = st.button("🔍 Buscar", use_container_width=True)

if enviar and prompt:
    with st.spinner("🌊 Kai está buscando..."):
        respuesta = responder(prompt, USUARIO)
    guardar_memoria(prompt, respuesta)
    st.session_state.historial = cargar_memoria()
    st.rerun()

with st.sidebar:
    st.markdown("### 🌊 Kai")
    st.markdown(f"**Usuario:** {USUARIO}")
    st.markdown("---")
    st.markdown("**Ejemplos:**")
    st.markdown("• redes neuronales")
    st.markdown("• inteligencia artificial")
    st.markdown("• dame código")
    st.markdown("---")
    if st.button("🗑️ Limpiar", use_container_width=True):
        st.session_state.historial = []
        if os.path.exists(MEMORIA_FILE):
            os.remove(MEMORIA_FILE)
        st.rerun()
