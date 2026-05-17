import streamlit as st
import requests

st.set_page_config(page_title="Kai - Asistente IA", layout="wide")

st.title("🌊 Kai - Asistente de IA")

# ========== CODIGOS PYTHON ==========
def dar_codigo_saludo():
    return "**Codigo Python - Saludo simple**\n\n```python\nnombre = input('¿Como te llamas? ')\nprint(f'¡Hola {nombre}! Bienvenido a Python')\n```"

def dar_codigo_red_neuronal():
    return "**Codigo Python - Red Neuronal Simple**\n\n```python\nimport numpy as np\n\nclass RedNeuronal:\n    def __init__(self, entradas, salidas):\n        self.pesos = np.random.randn(entradas, salidas) * 0.1\n    \n    def activacion(self, x):\n        return 1 / (1 + np.exp(-x))\n    \n    def predecir(self, entrada):\n        return self.activacion(np.dot(entrada, self.pesos))\n\nnn = RedNeuronal(2, 1)\nprint(f'Prediccion: {nn.predecir([0.5, 0.8])}')\n```"

# ========== FORMULA SISTEMA NO LINEAL ==========
def dar_formula_snl():
    return "**Sistemas No Lineales**\n\nNo existe una formula unica. Ejemplo:\n```\ndx/dt = x^2 - 1\ndy/dt = x*y + y\n```\nCaracteristica: La salida no es proporcional a la entrada.\n\nWikipedia: Sistema no lineal"

# ========== EXTRAER TEMA ==========
def extraer_tema(pregunta):
    p = pregunta.lower().strip()
    
    palabras_eliminar = [
        "puedes darme la", "puedes darme", "podrias darme", "dame la", "dame el",
        "cual es la", "cual es el", "que es", "que son", "explicame", "defineme",
        "como funciona", "formula de", "para que sirve", "necesito saber", "dime"
    ]
    
    for palabra in palabras_eliminar:
        p = p.replace(palabra, "")
    
    p = p.strip().strip("?¿!¡.:;")
    
    if "sistema no lineal" in p or "sistemas no lineales" in p:
        return "sistema no lineal"
    if "redes neurales" in p or "redes neuronales" in p:
        return "red neuronal artificial"
    if "inteligencia artificial" in p or "ia" in p:
        return "inteligencia artificial"
    
    return p if len(p) > 2 else ""

# ========== BUSCAR EN WIKIPEDIA ==========
def buscar_wikipedia(tema):
    if not tema or len(tema) < 3:
        return "¿Que quieres saber? Por ejemplo: 'sistema no lineal'"
    
    try:
        url = f"https://es.wikipedia.org/api/rest_v1/page/summary/{tema.replace(' ', '_')}"
        r = requests.get(url, headers={"User-Agent": "KaiBot"})
        
        if r.status_code == 200:
            data = r.json()
            if "extract" in data and data["extract"]:
                titulo = data.get("title", tema)
                extracto = data["extract"][:700]
                return f"**{titulo}**\n\n{extracto}\n\n📚 Wikipedia"
        
        return f"No encontre informacion sobre '{tema}'"
    except:
        return "Error de conexion. Intenta de nuevo."

# ========== DETECTAR INTENCION ==========
def detectar_intencion(mensaje):
    m = mensaje.lower()
    
    if "codigo" in m or "programa" in m:
        if "saludo" in m:
            return "codigo_saludo"
        return "codigo_red"
    
    if "formula" in m and "sistema no lineal" in m:
        return "formula_snl"
    
    if "hola" in m or "buenos" in m:
        return "saludo"
    
    if "gracias" in m or "excelente" in m or "genial" in m:
        return "aprobacion"
    
    return "definicion"

# ========== RESPUESTA PRINCIPAL ==========
def responder(mensaje, usuario):
    intencion = detectar_intencion(mensaje)
    
    if intencion == "saludo":
        return f"🌊 ¡Hola {usuario}! ¿Que quieres saber? Puedo darte formulas o codigo Python."
    
    if intencion == "aprobacion":
        return f"🌊 ¡Me alegra, {usuario}! ¿Necesitas algo mas?"
    
    if intencion == "codigo_saludo":
        return dar_codigo_saludo()
    
    if intencion == "codigo_red":
        return dar_codigo_red_neuronal()
    
    if intencion == "formula_snl":
        return dar_formula_snl()
    
    tema = extraer_tema(mensaje)
    return buscar_wikipedia(tema)

USUARIO = "Giovanni"

# ========== INTERFAZ ==========
if 'historial' not in st.session_state:
    st.session_state.historial = []

for msg in st.session_state.historial[-30:]:
    st.markdown(f"**👤 Tu:** {msg['usuario']}")
    st.markdown(f"**🌊 Kai:** {msg['respuesta']}")
    st.markdown("---")

prompt = st.text_input("", placeholder="Ej: ¿puedes darme la formula de sistema no lineal?", key="input_msg", label_visibility="collapsed")

if st.button("Enviar") and prompt:
    with st.spinner("Kai esta pensando..."):
        respuesta = responder(prompt, USUARIO)
    st.session_state.historial.append({"usuario": prompt, "respuesta": respuesta})
    st.rerun()

with st.sidebar:
    st.markdown("### 🌊 Kai")
    st.markdown("**Ejemplos:**")
    st.markdown("- ¿puedes darme la formula de sistema no lineal?")
    st.markdown("- define inteligencia artificial")
    st.markdown("- dame codigo de saludo")
    st.markdown("- hola")
    if st.button("Limpiar conversacion"):
        st.session_state.historial = []
        st.rerun()
