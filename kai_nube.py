# ============================================================
# kai_enhanced.py - Versión mejorada con 6 capacidades
# ============================================================

import streamlit as st
import google.generativeai as genai
import chromadb
import docker
import requests
import cv2
import numpy as np
from sentence_transformers import SentenceTransformer
from sympy import symbols, sympify, solve, diff, integrate, simplify
from datetime import datetime
import hashlib
import json
import time
import re
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from PIL import Image
import io
import base64

# ============================================================
# CONFIGURACIÓN INICIAL
# ============================================================

st.set_page_config(page_title="Kai - Asistente Evolucionado", layout="wide")
st.title("🌊 Kai - Asistente con IA (v2.0)")

# Inicializar Gemini
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
    st.sidebar.success("✅ Gemini conectado")
except Exception as e:
    st.error(f"Error de conexión con Gemini: {e}")
    st.stop()

# ============================================================
# PUNTO 1: MEMORIA PERSISTENTE (ChromaDB + Embeddings)
# ============================================================

class MemorySystem:
    def __init__(self):
        self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection("kai_memory")
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')

    def store(self, user_id, prompt, response, metadata=None):
        """Almacena una interacción en memoria persistente"""
        text = f"Usuario: {prompt}\nKai: {response}"
        embedding = self.encoder.encode(text).tolist()
        doc_id = f"{user_id}_{int(time.time())}_{hashlib.md5(text.encode()).hexdigest()[:8]}"

        meta = {
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "prompt_length": len(prompt),
            **({"custom": metadata} if metadata else {})
        }

        self.collection.add(
            embeddings=[embedding],
            documents=[text],
            metadatas=[meta],
            ids=[doc_id]
        )
        return doc_id

    def recall(self, user_id, query, n=5):
        """Recupera interacciones relevantes del pasado"""
        q_emb = self.encoder.encode(query).tolist()
        results = self.collection.query(
            query_embeddings=[q_emb],
            n_results=n,
            where={"user_id": user_id}
        )

        if results['documents']:
            return [{
                "text": doc,
                "score": score,
                "metadata": meta
            } for doc, score, meta in zip(
                results['documents'][0],
                results['distances'][0],
                results['metadatas'][0]
            )]
        return []

# ============================================================
# PUNTO 2: SANDBOX DE EJECUCIÓN DE CÓDIGO
# ============================================================

class CodeSandbox:
    def __init__(self):
        self.client = docker.from_env()
        self.image = "python:3.11-slim"

    def execute(self, code, timeout=10):
        """Ejecuta código Python en un contenedor aislado"""
        try:
            # Sanitizar código para evitar inyección
            sanitized = code.replace("'", "'\"'\"'")

            container = self.client.containers.run(
                image=self.image,
                command=f"python -c '{sanitized}'",
                detach=True,
                mem_limit="256m",
                cpu_period=100000,
                cpu_quota=50000,
                network_disabled=True,
                remove=True
            )

            result = container.wait(timeout=timeout)
            logs = container.logs(stdout=True, stderr=True).decode()

            return {
                "success": result["StatusCode"] == 0,
                "output": logs,
                "error": None if result["StatusCode"] == 0 else logs
            }
        except docker.errors.DockerException as e:
            return {"success": False, "output": "", "error": f"Docker error: {str(e)}"}
        except Exception as e:
            return {"success": False, "output": "", "error": str(e)}

# ============================================================
# PUNTO 3: CONOCIMIENTO ACTUALIZADO AUTOMÁTICAMENTE
# ============================================================

class KnowledgeUpdater:
    def __init__(self):
        self.cache = {}
        self.last_update = {}

    def search_web(self, query, max_results=3):
        """Busca información actualizada en la web"""
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
            return [{"title": r["title"], "body": r["body"], "href": r["href"]} for r in results]
        except Exception as e:
            return [{"title": "Error", "body": f"No se pudo buscar: {str(e)}", "href": ""}]

    def get_relevant_knowledge(self, query, force_refresh=False):
        """Obtiene conocimiento actualizado, con caché"""
        cache_key = hashlib.md5(query.encode()).hexdigest()

        if cache_key in self.cache and not force_refresh:
            if time.time() - self.last_update[cache_key] < 3600:  # 1 hora de caché
                return self.cache[cache_key]

        results = self.search_web(query)
        self.cache[cache_key] = results
        self.last_update[cache_key] = time.time()
        return results

# ============================================================
# PUNTO 4: ANÁLISIS MULTIMODAL TÉCNICO
# ============================================================

class MultimodalAnalyzer:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )

    def analyze_image(self, image):
        """Analiza una imagen y extrae información técnica"""
        img_array = np.array(image)

        # Detección de rostros
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)

        # Análisis básico
        height, width, channels = img_array.shape
        mean_color = np.mean(img_array, axis=(0, 1))
        brightness = np.mean(gray)

        return {
            "dimensions": f"{width}x{height}",
            "channels": channels,
            "mean_color_rgb": mean_color.tolist(),
            "brightness": float(brightness),
            "faces_detected": len(faces)
        }

    def analyze_code_image(self, image):
        """Intenta extraer texto de código de una imagen"""
        # Aquí se podría integrar OCR (Tesseract)
        return {"extracted_text": "OCR no implementado aún"}

# ============================================================
# PUNTO 5: RAZONAMIENTO MATEMÁTICO FORMAL
# ============================================================

class MathEngine:
    def __init__(self):
        self.operators = {
            'derivative': self._derivative,
            'integral': self._integral,
            'solve': self._solve_equation,
            'simplify': self._simplify_expression,
            'limit': self._limit
        }

    def _derivative(self, expr, var='x'):
        x = symbols(var)
        expr_sym = sympify(expr)
        return str(diff(expr_sym, x))

    def _integral(self, expr, var='x'):
        x = symbols(var)
        expr_sym = sympify(expr)
        return str(integrate(expr_sym, x))

    def _solve_equation(self, expr, var='x'):
        x = symbols(var)
        expr_sym = sympify(expr)
        return [str(s) for s in solve(expr_sym, x)]

    def _simplify_expression(self, expr):
        expr_sym = sympify(expr)
        return str(simplify(expr_sym))

    def _limit(self, expr, var='x', point=0):
        x = symbols(var)
        expr_sym = sympify(expr)
        from sympy import limit
        return str(limit(expr_sym, x, point))

    def solve(self, query):
        """Detecta y resuelve operaciones matemáticas"""
        # Patrones de detección
        patterns = {
            'derivative': r'(derivada|diferenciar)\s+de\s+(.+?)(?:\s+respecto\s+a\s+(\w))?$',
            'integral': r'(integral|integrar)\s+(.+?)(?:\s+respecto\s+a\s+(\w))?$',
            'solve': r'(resolver|solucionar|solve)\s+(.+?)(?:\s+para\s+(\w))?$',
            'simplify': r'(simplificar|simplify)\s+(.+?)$',
            'limit': r'(límite|limite|limit)\s+de\s+(.+?)(?:\s+cuando\s+(\w)\s*->\s*([\d.]+))?$'
        }

        for op, pattern in patterns.items():
            match = re.match(pattern, query, re.IGNORECASE)
            if match:
                groups = match.groups()
                if op in ['derivative', 'integral']:
                    expr = groups[1]
                    var = groups[2] if groups[2] else 'x'
                    return self.operators[op](expr, var)
                elif op == 'solve':
                    expr = groups[1]
                    var = groups[2] if groups[2] else 'x'
                    return self.operators[op](expr, var)
                elif op == 'simplify':
                    return self.operators[op](groups[1])
                elif op == 'limit':
                    expr = groups[1]
                    var = groups[2] if groups[2] else 'x'
                    point = float(groups[3]) if groups[3] else 0
                    return self.operators[op](expr, var, point)

        return None  # No es una consulta matemática

# ============================================================
# PUNTO 6: COLABORACIÓN MULTIAGENTE
# ============================================================

class AgentOrchestrator:
    def __init__(self, memory, sandbox, knowledge, math_engine):
        self.agents = {
            "code": sandbox,
            "knowledge": knowledge,
            "math": math_engine
        }
        self.memory = memory

    def process_query(self, user_id, query):
        """Distribuye la consulta al agente adecuado"""
        # Detectar tipo de consulta
        if self._is_code_query(query):
            return self._handle_code(query)
        elif self._is_math_query(query):
            return self._handle_math(query)
        elif self._is_knowledge_query(query):
            return self._handle_knowledge(query)
        else:
            return None  # Dejar que Gemini maneje

    def _is_code_query(self, query):
        patterns = [
            r'```python',
            r'ejecuta.*código',
            r'corre.*script',
            r'run.*code',
            r'execute.*python'
        ]
        return any(re.search(p, query, re.IGNORECASE) for p in patterns)

    def _is_math_query(self, query):
        patterns = [
            r'derivada|integral|límite|resolver.*=',
            r'solve|differentiate|integrate|limit',
            r'\b\d+\s*[\+\-\*/]\s*\d+'
        ]
        return any(re.search(p, query, re.IGNORECASE) for p in patterns)

    def _is_knowledge_query(self, query):
        patterns = [
            r'últimas? noticias',
            r'actualizado|reciente',
            r'qué ha pasado',
            r'latest|news|update'
        ]
        return any(re.search(p, query, re.IGNORECASE) for p in patterns)

    def _handle_code(self, query):
        code = self._extract_code(query)
        if code:
            return self.agents["code"].execute(code)
        return None

    def _handle_math(self, query):
        return self.agents["math"].solve(query)

    def _handle_knowledge(self, query):
        return self.agents["knowledge"].get_relevant_knowledge(query)

    def _extract_code(self, text):
        match = re.search(r'```python\n?(.*?)```', text, re.DOTALL)
        return match.group(1).strip() if match else None

# ============================================================
# INICIALIZACIÓN DE MÓDULOS
# ============================================================

# Inicializar en sidebar
with st.sidebar:
    st.header("🔧 Módulos Activos")

    memory = MemorySystem()
    st.success("✅ Memoria persistente")

    try:
        sandbox = CodeSandbox()
        st.success("✅ Sandbox de código")
    except:
        sandbox = None
        st.warning("⚠️ Sandbox no disponible (Docker requerido)")

    knowledge = KnowledgeUpdater()
    st.success("✅ Conocimiento web")

    analyzer = MultimodalAnalyzer()
    st.success("✅ Análisis multimodal")

    math_engine = MathEngine()
    st.success("✅ Motor matemático")

    orchestrator = AgentOrchestrator(memory, sandbox, knowledge, math_engine)
    st.success("✅ Orquestador multiagente")

# ============================================================
# INTERFAZ DE CHAT PRINCIPAL
# ============================================================

# Inicializar historial
if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_id" not in st.session_state:
    st.session_state.user_id = "default_user"

# Mostrar mensajes anteriores
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "metadata" in message:
            with st.expander("📊 Detalles técnicos"):
                st.json(message["metadata"])

# Input del usuario
if prompt := st.chat_input("Escribe tu mensaje aquí (o sube una imagen)..."):

    # Mostrar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Procesar respuesta
    with st.chat_message("assistant"):
        with st.spinner("🧠 Procesando..."):

            # 1. Verificar memoria relevante
            context = memory.recall(st.session_state.user_id, prompt)

            # 2. Intentar con agentes especializados
            agent_result = orchestrator.process_query(
                st.session_state.user_id, prompt
            )

            if agent_result:
                # Si un agente especializado respondió
                if isinstance(agent_result, dict):
                    if agent_result.get("success"):
                        response_text = f"```\n{agent_result['output']}\n```"
                    else:
                        response_text = f"❌ Error: {agent_result.get('error', 'Desconocido')}"
                elif isinstance(agent_result, list):
                    response_text = "\n\n".join([
                        f"**{r.get('title', 'Resultado')}**\n{r.get('body', str(r))}" 
                        for r in agent_result
                    ])
                else:
                    response_text = str(agent_result)
            else:
                # 3. Si no, usar Gemini con contexto
                enhanced_prompt = prompt

                if context:
                    enhanced_prompt = (
                        f"[Contexto de conversaciones previas]:\n"
                        f"{chr(10).join([c['text'][:200] for c in context])}\n\n"
                        f"[Consulta actual]: {prompt}"
                    )

                response = model.generate_content(enhanced_prompt)
                response_text = response.text

            # Mostrar respuesta
            st.markdown(response_text)

            # 4. Almacenar en memoria
            memory.store(
                st.session_state.user_id,
                prompt,
                response_text,
                metadata={"agent_used": "gemini" if not agent_result else "specialized"}
            )

    # Guardar en historial
    st.session_state.messages.append({"role": "assistant", "content": response_text})

# ============================================================
# SUBIDA DE IMÁGENES (Punto 4)
# ============================================================

with st.sidebar:
    st.header("📷 Subir imagen")
    uploaded_file = st.file_uploader(
        "Selecciona una imagen", 
        type=['png', 'jpg', 'jpeg']
    )

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Imagen cargada", use_column_width=True)

        if st.button("🔍 Analizar imagen"):
            with st.spinner("Analizando..."):
                analysis = analyzer.analyze_image(image)
                st.json(analysis)

                # Añadir al chat
                analysis_text = f"**Análisis de imagen:**\n```json\n{json.dumps(analysis, indent=2)}\n```"
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": analysis_text,
                    "metadata": analysis
                })

# ============================================================
# CONTROLES ADICIONALES
# ============================================================

with st.sidebar:
    st.header("⚙️ Controles")

    if st.button("🗑️ Limpiar memoria"):
        st.session_state.messages = []
        st.rerun()

    if st.button("🔄 Forzar actualización de conocimiento"):
        knowledge.cache = {}
        st.success("Caché de conocimiento limpiada")

    user_id_input = st.text_input(
        "ID de usuario", 
        value=st.session_state.user_id
    )
    if user_id_input != st.session_state.user_id:
        st.session_state.user_id = user_id_input
        st.rerun()

# ============================================================
# PIE DE PÁGINA
# ============================================================

st.markdown("---")
st.caption(
    "🌊 Kai v2.0 - Asistente con Memoria Persistente, "
    "Ejecución de Código, Conocimiento Web, "
    "Análisis Multimodal, Motor Matemático y "
    "Orquestación Multiagente"
)
