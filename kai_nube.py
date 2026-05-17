# kai_nube.py - Búsqueda de definiciones CORREGIDA
import streamlit as st
import requests

st.set_page_config(page_title="Kai - Asistente IA", layout="wide")

st.title("🌊 Kai - Asistente de IA")
st.markdown("Puedo: **definir conceptos**, **dar código Python**, **explicar temas** y **conversar**.")

# ========== BASE DE CONOCIMIENTO ==========
def dar_codigo_generico(tema):
    tema_lower = tema.lower()
    
    if "hola" in tema_lower or "saludo" in tema_lower:
        return """**Código Python - Saludo simple**

```python
nombre = input("¿Cómo te llamas? ")
print(f"¡Hola {nombre}! Bienvenido a Python")
```"""

    if "calculadora" in tema_lower or "suma" in tema_lower:
        return """**Código Python - Calculadora simple**

```python
def calculadora():
    print("1. Suma")
    print("2. Resta")
    opcion = input("Elige opción: ")
    a = float(input("Primer número: "))
    b = float(input("Segundo número: "))
    
    if opcion == "1":
        print(f"Resultado: {a + b}")
    elif opcion == "2":
        print(f"Resultado: {a - b}")

calculadora()
```"""

    if "lista" in tema_lower or "array" in tema_lower:
        return """**Código Python - Listas y bucles**

```python
frutas = ["manzana", "pera", "uva", "naranja"]
for fruta in frutas:
    print(f"- {fruta}")
```"""

    return dar_codigo_red_neuronal()

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
entrada = np.array([0.5, 0.8])
print(f"Predicción: {nn.predecir(entrada)}")
```"""

# ========== DETECTAR INTENCIÓN ==========
def detectar_intencion(mensaje):
    m = mensaje.lower()
    
    # 1. Código Python
    if any(p in m for p in ["codigo", "código", "programa", "script", "dame un", "dame codigo", "escribe un"]):
        return "codigo"
    
    # 2. Saludos
    if any(p in m for p in ["hola", "buenos dias", "buenas tardes", "buenas noches", "saludos"]):
        return "saludo"
    
    # 3. Aprobación/agradecimiento
    if any(p in m for p in ["excelente", "perfecto", "genial", "gracias", "bien", "me gusta"]):
        return "aprobacion"
    
    # 4. Definición (¡CORREGIDO!)
    if any(p in m for p in ["define", "definición", "significado", "que es", "qué es", 
                            "que son", "qué son", "dime que", "explica que", "explicame que"]):
        return "definicion"
    
    # 5. Por defecto
    return "definicion"

# ========== EXTRAER TÉRMINO DE BÚSQUEDA ==========
def extraer_termino(mensaje):
    m = mensaje.lower().strip()
    
    # Eliminar frases comunes
    eliminar = [
        "define", "definición", "definicion", "significado",
        "dime que", "explica que", "explicame que", "que es", "qué es",
        "que son", "qué son", "buscame", "busca", "encuentrame", "investiga"
    ]
    
    for e in eliminar:
        m = m.replace(e, "")
    
    # Limpiar
    m = m.strip().strip(" ?.,;:!¿¡")
    
    # Correcciones ortográficas
    if "redes neurales" in m or "neurales" in m:
        m = "redes neuronales"
    if m == "redes neuronales":
        m = "red neuronal artificial"
    
    return m if len(m) > 2 else ""

# ========== BÚSQUEDA EN WIKIPEDIA ==========
def buscar_definicion(termino):
    if not termino or len(termino) < 3:
        return "¿Qué quieres que defina? Por ejemplo: 'inteligencia artificial', 'redes neuronales'"
    
    try:
        url = f"https://es.wikipedia.org/api/rest_v1/page/summary/{termino.replace(' ', '_')}"
        r = requests.get(url, headers={"User-Agent": "KaiBot"})
        
        if r.status_code == 200:
            data = r.json()
            titulo = data.get('title', termino)
            extracto = data.get('extract', '')[:700]
            return f"**{titulo}**\n\n{extracto}\n\n📚 Fuente: Wikipedia"
        
        # Búsqueda alternativa
        url_buscar = f"https://es.wikipedia.org/w/api.php?action=query&list=search&srsearch={termino}&format=json&origin=*"
        r = requests.get(url_buscar, headers={"User-Agent": "KaiBot"})
        if r.status_code == 200:
            data = r.json()
            resultados = data.get("query", {}).get("search", [])
            if resultados:
                primer = resultados[0]["title"]
                return f"No encontré '{termino}'. ¿Quizás te refieres a **{primer}**? Escríbelo para buscarlo."
        
        return f"No encontré información sobre '{termino}'. Prueba con 'inteligencia artificial' o 'redes neuronales'."
    except:
        return "Error de conexión. Intenta de nuevo."

# ========== RESPUESTAS ==========
def responder(mensaje, usuario):
    intencion = detectar_intencion(mensaje)
    
    if intencion == "saludo":
        return f"🌊 ¡Hola {usuario}! Puedo **definir conceptos** (ej: 'define inteligencia artificial') o **dar código Python** (ej: 'dame código de saludo'). 😊"
    
    if intencion == "aprobacion":
        return f"🌊 ¡Me alegra que te sea útil, {usuario}! ¿Necesitas alguna definición o código más? 💙"
    
    if intencion == "codigo":
        return dar_codigo_generico(mensaje)
    
    # Definición (intención por defecto)
    termino = extraer_termino(mensaje)
    return buscar_definicion(termino)

# ========== INTERFAZ ==========
if 'historial' not in st.session_state:
    st.session_state.historial = []

for msg in st.session_state.historial[-30:]:
    st.markdown(f"**👤 Tú:** {msg['usuario']}")
    st.markdown(f"**🌊 Kai:** {msg['respuesta']}")
    st.markdown("---")

prompt = st.text_input("", placeholder="Ej: define inteligencia artificial / dame código de saludo / redes neuronales", key="input_msg", label_visibility="collapsed")

if st.button("Enviar") and prompt:
    with st.spinner("Kai está pensando..."):
        respuesta = responder(prompt, "Giovanni")
    st.session_state.historial.append({"usuario": prompt, "respuesta": respuesta})
    st.rerun()

with st.sidebar:
    st.markdown("### 🌊 Kai")
    st.markdown("**Ejemplos:**")
    st.markdown("• define inteligencia artificial")
    st.markdown("• qué son redes neuronales")
    st.markdown("• dame código de saludo")
    st.markdown("• hola")
    st.markdown("---")
    if st.button("Limpiar conversación"):
        st.session_state.historial = []
        st.rerun()
