con **f(·)** siendo una función **no lineal**.

**Encontrarás más detalles en:** Wikipedia: **Sistema no lineal**"""

# ========== DETECTAR INTENCIÓN ==========
def detectar_intencion(mensaje):
    m = mensaje.lower()
    
    if any(p in m for p in ["codigo", "código", "programa", "dame un"]):
        return "codigo"
    
    if "formula" in m or "fórmula" in m:
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
    m = mensaje.lower()
    
    if intencion == "saludo":
        return f"🌊 ¡Hola {usuario}! Pregúntame sobre **sistemas no lineales**, **inteligencia artificial** o pídeme **código Python**. 😊"
    
    if intencion == "aprobacion":
        return f"🌊 ¡Me alegra, {usuario}! ¿Necesitas alguna fórmula o concepto más? 💙"
    
    if intencion == "codigo":
        return dar_codigo_generico(mensaje)
    
    if intencion == "formula_snl":
        return dar_formula_sistema_no_lineal()
    
    # Extraer tema y buscar
    tema = extraer_tema(mensaje)
    return buscar_en_wikipedia(tema, usuario)

# ========== INTERFAZ ==========
if 'historial' not in st.session_state:
    st.session_state.historial = []

for msg in st.session_state.historial[-30:]:
    st.markdown(f"**👤 Tú:** {msg['usuario']}")
    st.markdown(f"**🌊 Kai:** {msg['respuesta']}")
    st.markdown("---")

prompt = st.text_input("", placeholder="Ej: ¿puedes darme la fórmula de sistema no lineal? / define inteligencia artificial / hola", key="input_msg", label_visibility="collapsed")

if st.button("Enviar") and prompt:
    with st.spinner("Kai está pensando..."):
        respuesta = responder(prompt, "Giovanni")
    st.session_state.historial.append({"usuario": prompt, "respuesta": respuesta})
    st.rerun()

with st.sidebar:
    st.markdown("### 🌊 Kai")
    st.markdown("**Ejemplos:**")
    st.markdown("• ¿puedes darme la fórmula de sistema no lineal?")
    st.markdown("• define inteligencia artificial")
    st.markdown("• qué son redes neuronales")
    st.markdown("• dame código de saludo")
    st.markdown("---")
    if st.button("Limpiar conversación"):
        st.session_state.historial = []
        st.rerun()
