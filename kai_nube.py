con f() siendo una funcion no lineal.

**Encontraras mas detalles en:** Wikipedia: Sistema no lineal
"""

# ========== EXTRAER TERMINO ==========
def extraer_tema(pregunta):
    p = pregunta.lower().strip()
    
    eliminar = [
        "puedes darme la", "puedes darme", "podrias darme", "dame la", "dame el",
        "cual es la", "cual es el", "que es", "que son", "explicame", "defineme",
        "como funciona", "formula de", "para que sirve", "necesito saber", "quisiera saber", "dime"
    ]
    
    for e in eliminar:
        p = p.replace(e, "")
    
    p = p.strip().strip("?¿!¡.:;")
    
    mapeo = {
        "sistema no lineal": "sistema no lineal",
        "sistemas no lineales": "sistema no lineal",
        "redes neurales": "redes neuronales",
        "red neuronal": "red neuronal artificial",
        "ia": "inteligencia artificial"
    }
    
    for clave, valor in mapeo.items():
        if clave in p:
            return valor
    
    return p if len(p) > 2 else ""

# ========== BUSQUEDA EN WIKIPEDIA ==========
def buscar_en_wikipedia(tema, usuario):
    if not tema or len(tema) < 3:
        return f"🌊 {usuario}, ¿que quieres saber? Por ejemplo: 'sistema no lineal', 'inteligencia artificial'"
    
    try:
        url = f"https://es.wikipedia.org/api/rest_v1/page/summary/{tema.replace(' ', '_')}"
        r = requests.get(url, headers={"User-Agent": "KaiBot"})
        
        if r.status_code == 200:
            data = r.json()
            if "extract" in data and data["extract"]:
                titulo = data.get("title", tema)
                extracto = data["extract"][:800]
                return f"**{titulo}**\n\n{extracto}\n\n📚 Wikipedia"
        
        url_buscar = f"https://es.wikipedia.org/w/api.php?action=query&list=search&srsearch={tema}&format=json&origin=*"
        r = requests.get(url_buscar, headers={"User-Agent": "KaiBot"})
        if r.status_code == 200:
            data = r.json()
            resultados = data.get("query", {}).get("search", [])
            if resultados:
                primer = resultados[0]["title"]
                snippet = resultados[0].get("snippet", "")[:500]
                return f"**{primer}**\n\n{snippet}\n\n📚 Wikipedia"
        
        return f"No encontre informacion sobre '{tema}'. Prueba con 'sistema no lineal'."
    except:
        return "Error de conexion. Intenta de nuevo."

# ========== DETECTAR INTENCION ==========
def detectar_intencion(mensaje):
    m = mensaje.lower()
    
    if any(p in m for p in ["codigo", "codigo", "programa", "dame un"]):
        return "codigo"
    
    if "formula" in m or "formula" in m:
        if "sistema no lineal" in m:
            return "formula_snl"
    
    if any(p in m for p in ["hola", "buenos dias", "buenas tardes"]):
        return "saludo"
    
    if any(p in m for p in ["excelente", "gracias", "genial", "perfecto"]):
        return "aprobacion"
    
    return "definicion"

# ========== RESPUESTAS ==========
def responder(mensaje, usuario):
    intencion = detectar_intencion(mensaje)
    
    if intencion == "saludo":
        return f"🌊 ¡Hola {usuario}! Preguntame sobre sistemas no lineales, inteligencia artificial o pideme codigo Python. 😊"
    
    if intencion == "aprobacion":
        return f"🌊 ¡Me alegra, {usuario}! ¿Necesitas alguna formula o concepto mas? 💙"
    
    if intencion == "codigo":
        return dar_codigo_generico(mensaje)
    
    if intencion == "formula_snl":
        return dar_formula_sistema_no_lineal()
    
    tema = extraer_tema(mensaje)
    return buscar_en_wikipedia(tema, usuario)

USUARIO = "Giovanni"

# ========== INTERFAZ ==========
if 'historial' not in st.session_state:
    st.session_state.historial = []

for msg in st.session_state.historial[-30:]:
    st.markdown(f"**👤 Tu:** {msg['usuario']}")
    st.markdown(f"**🌊 Kai:** {msg['respuesta']}")
    st.markdown("---")

prompt = st.text_input("", placeholder="Ej: ¿puedes darme la formula de sistema no lineal? / define inteligencia artificial / hola", key="input_msg", label_visibility="collapsed")

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
    st.markdown("- que son redes neuronales")
    st.markdown("- dame codigo de saludo")
    st.markdown("---")
    if st.button("Limpiar conversacion"):
        st.session_state.historial = []
        st.rerun()
