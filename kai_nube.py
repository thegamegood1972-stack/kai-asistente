# kai_nube.py - Versión que responde TODO tipo de solicitud
import streamlit as st
import requests

st.set_page_config(page_title="Kai - Asistente IA", layout="wide")

st.title("🌊 Kai - Asistente de IA")
st.markdown("Puedo: **dar código Python**, **definir conceptos**, **explicar temas** y **conversar**.")

# ========== BASE DE CONOCIMIENTO ==========
def dar_codigo_generico(tema):
    """Devuelve código Python según el tema solicitado"""
    tema_lower = tema.lower()
    
    if "hola" in tema_lower or "saludo" in tema_lower:
        return """**Código Python - Saludo simple**

```python
# Programa de saludo en Python
nombre = input("¿Cómo te llamas? ")
print(f"¡Hola {nombre}! Bienvenido a Python")
```"""

    if "calculadora" in tema_lower or "suma" in tema_lower:
        return """**Código Python - Calculadora simple**

```python
# Calculadora básica
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
# Ejemplo de listas en Python
frutas = ["manzana", "pera", "uva", "naranja"]

print("Mis frutas favoritas:")
for fruta in frutas:
    print(f"- {fruta}")

# Agregar una fruta
frutas.append("sandía")
print(f"\\nAhora tengo {len(frutas)} frutas")
```"""

    if "red neuronal" in tema_lower or "neural" in tema_lower:
        return dar_codigo_red_neuronal()
    
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

def dar_explicacion():
    return """**¿Cómo funciona una red neuronal?**

Una red neuronal artificial aprende ajustando sus "pesos" (conexiones entre neuronas). El proceso es:

1. **Entrada:** Recibe datos (ej: píxeles de una imagen)
2. **Propagación:** La señal viaja a través de las capas
3. **Cálculo del error:** Compara su predicción con la respuesta correcta
4. **Ajuste (retropropagación):** Modifica los pesos para mejorar
5. **Repite:** Hasta que el error sea pequeño

**Analogía:** Es como aprender a andar en bicicleta. Al principio te caes (error), pero ajustas tu equilibrio (pesos) hasta que lo logras."""

# ========== DETECTAR INTENCIÓN MEJORADA ==========
def detectar_intencion(mensaje):
    m = mensaje.lower()
    
    # 1. Código Python (cualquier solicitud de código)
    if any(p in m for p in ["codigo", "código", "programa", "script", "implementar", 
                            "dame un", "dame codigo", "escribe un", "crea un"]):
        return "codigo"
    
    # 2. Explicación didáctica
    if any(p in m for p in ["explica", "cómo funciona", "explicame", "qué es"]):
        return "explicacion"
    
    # 3. Saludos
    if any(p in m for p in ["hola", "buenos dias", "buenas tardes", "buenas noches", "saludos"]):
        return "saludo"
    
    # 4. Aprobación/agradecimiento
    if any(p in m for p in ["excelente", "perfecto", "genial", "gracias", "bien", "me gusta"]):
        return "aprobacion"
    
    # 5. Información/conceptos
    if any(p in m for p in ["que es", "que son", "definición", "significado"]):
        return "definicion"
    
    # 6. Por defecto: buscar información
    return "buscar"

# ========== CORRECCIÓN ORTOGRÁFICA ==========
def corregir_termino(termino):
    t = termino.lower().strip()
    correcciones = {
        "redes neurales": "redes neuronales",
        "neurales": "neuronales",
    }
    for incorrecto, correcto in correcciones.items():
        if incorrecto in t:
            return correcto
    return t

def extraer_termino(mensaje):
    m = mensaje.lower()
    for p in ["buscame", "busca", "encuentrame", "todo lo relacionado con", "que es", "que son", "definicion de"]:
        m = m.replace(p, "")
    m = m.strip(" ?.,;:!").strip()
    return corregir_termino(m) if len(m) > 3 else m

# ========== BÚSQUEDA EN WIKIPEDIA ==========
def buscar_wikipedia(termino):
    if not termino or len(termino) < 3:
        return "¿Qué quieres buscar? Por ejemplo: 'redes neuronales', 'inteligencia artificial'"
    
    if termino == "redes neuronales":
        termino = "red neuronal artificial"
    
    try:
        url = f"https://es.wikipedia.org/api/rest_v1/page/summary/{termino.replace(' ', '_')}"
        r = requests.get(url, headers={"User-Agent": "KaiBot"})
        if r.status_code == 200:
            data = r.json()
            return f"**{data.get('title', termino)}**\n\n{data.get('extract', '')[:700]}\n\n📚 Fuente: Wikipedia"
        return f"No encontré información sobre '{termino}'. Prueba con otro término."
    except:
        return "Error de conexión. Intenta de nuevo."

# ========== RESPUESTAS ==========
def responder(mensaje, usuario):
    intencion = detectar_intencion(mensaje)
    
    # Saludos
    if intencion == "saludo":
        return f"🌊 ¡Hola {usuario}! Puedes pedirme **código Python** (ej: 'dame código de saludo'), **definiciones** (ej: 'qué es IA') o **explicaciones**. 😊"
    
    # Aprobación
    if intencion == "aprobacion":
        return f"🌊 ¡Me alegra que te guste, {usuario}! ¿Necesitas algo más? Puedo darte más ejemplos de código. 💙"
    
    # Código Python
    if intencion == "codigo":
        return dar_codigo_generico(mensaje)
    
    # Explicación didáctica
    if intencion == "explicacion":
        if "red neuronal" in mensaje.lower() or "neural" in mensaje.lower():
            return dar_explicacion()
        else:
            return buscar_wikipedia(extraer_termino(mensaje))
    
    # Búsqueda normal
    termino = extraer_termino(mensaje)
    return buscar_wikipedia(termino)

# ========== INTERFAZ ==========
if 'historial' not in st.session_state:
    st.session_state.historial = []

for msg in st.session_state.historial[-30:]:
    st.markdown(f"**👤 Tú:** {msg['usuario']}")
    st.markdown(f"**🌊 Kai:** {msg['respuesta']}")
    st.markdown("---")

prompt = st.text_input("", placeholder="Ej: dame código de saludo / qué es inteligencia artificial / redes neuronales / hola", key="input_msg", label_visibility="collapsed")

if st.button("Enviar") and prompt:
    with st.spinner("Kai está pensando..."):
        respuesta = responder(prompt, "Giovanni")
    st.session_state.historial.append({"usuario": prompt, "respuesta": respuesta})
    st.rerun()

with st.sidebar:
    st.markdown("### 🌊 Kai")
    st.markdown("**Ejemplos:**")
    st.markdown("• dame código de saludo")
    st.markdown("• dame código de calculadora")
    st.markdown("• qué es inteligencia artificial")
    st.markdown("• redes neuronales")
    st.markdown("• hola")
    st.markdown("---")
    if st.button("Limpiar conversación"):
        st.session_state.historial = []
        st.rerun()
