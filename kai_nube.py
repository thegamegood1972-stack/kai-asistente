# ============================================================
# kai_v3_self_improving.py - Versión con Auto-Mejora Inteligente
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
import asyncio
from collections import defaultdict
from typing import List, Dict, Any, Optional
import statistics

# ============================================================
# CONFIGURACIÓN INICIAL
# ============================================================

st.set_page_config(page_title="Kai - Asistente Auto-Aprendizaje", layout="wide")
st.title("🧠 Kai - Asistente con Auto-Mejora Inteligente (v3.0)")

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
    
    def get_all_interactions(self, user_id=None):
        """Recupera todas las interacciones para análisis"""
        if user_id:
            results = self.collection.get(where={"user_id": user_id})
        else:
            results = self.collection.get()
        return results.get('documents', []), results.get('metadatas', [])

# ============================================================
# PUNTO 2: SANDBOX DE EJECUCIÓN DE CÓDIGO
# ============================================================

class CodeSandbox:
    def __init__(self):
        try:
            self.client = docker.from_env()
            self.image = "python:3.11-slim"
            self.available = True
        except:
            self.available = False

    def execute(self, code, timeout=10):
        """Ejecuta código Python en un contenedor aislado"""
        if not self.available:
            return {"success": False, "output": "", "error": "Docker no disponible"}
        
        try:
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
        except Exception as e:
            return {"success": False, "output": "", "error": str(e)}

# ============================================================
# PUNTO 3: CONOCIMIENTO ACTUALIZADO AUTOMÁTICAMENTE
# ============================================================

class KnowledgeUpdater:
    def __init__(self):
        self.cache = {}
        self.last_update = {}
        self.topic_interest = defaultdict(int)

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
            if time.time() - self.last_update[cache_key] < 3600:
                return self.cache[cache_key]
        
        results = self.search_web(query)
        self.cache[cache_key] = results
        self.last_update[cache_key] = time.time()
        self.topic_interest[query] += 1
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
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
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
        return None

# ============================================================
# PUNTO 6: SISTEMA DE FEEDBACK Y APRENDIZAJE
# ============================================================

class LearningSystem:
    def __init__(self, memory):
        self.memory = memory
        self.feedback_log = []
        self.performance_metrics = defaultdict(list)
        
    def collect_feedback(self, user_id, prompt, response, user_rating):
        """Recolecta y aprende de feedback explícito"""
        feedback_entry = {
            "user_id": user_id,
            "prompt": prompt,
            "response": response,
            "rating": user_rating,
            "timestamp": datetime.now().isoformat()
        }
        self.feedback_log.append(feedback_entry)
        self.performance_metrics[user_id].append(user_rating)
        
        # Aprender de bajas calificaciones
        if user_rating < 3:
            self._improve_response_pattern(prompt, response)
        
        # Almacenar en memoria persistente
        self.memory.store(user_id, prompt, response, 
                         metadata={"feedback": user_rating, "type": "user_feedback"})
        return True
    
    def _improve_response_pattern(self, bad_prompt, bad_response):
        """Analiza respuestas malas para mejorar"""
        patterns = {
            "too_vague": len(bad_response.split()) < 20,
            "off_topic": self._check_relevance(bad_prompt, bad_response),
            "incorrect_format": not self._check_formatting(bad_response)
        }
        # Almacenar para ajuste futuro
        self.memory.store("learning_system", bad_prompt, bad_response, 
                         metadata={"failed": True, "patterns": patterns})
    
    def _check_relevance(self, prompt, response):
        """Verifica relevancia básica"""
        prompt_words = set(prompt.lower().split())
        response_words = set(response.lower().split())
        overlap = len(prompt_words & response_words) / max(len(prompt_words), 1)
        return overlap < 0.2
    
    def _check_formatting(self, response):
        """Verifica formato adecuado"""
        has_code = '```' in response
        has_lists = re.search(r'^\s*[\*\-\+]', response, re.MULTILINE) is not None
        return has_code or has_lists or len(response.split()) > 50
    
    def get_average_rating(self, user_id=None):
        """Obtiene calificación promedio"""
        if user_id and user_id in self.performance_metrics:
            ratings = self.performance_metrics[user_id]
            return statistics.mean(ratings) if ratings else 0
        all_ratings = [r for ratings in self.performance_metrics.values() for r in ratings]
        return statistics.mean(all_ratings) if all_ratings else 0

# ============================================================
# PUNTO 7: OPTIMIZADOR DE PROMPTS (Auto-Prompt Engineering)
# ============================================================

class PromptOptimizer:
    def __init__(self, model):
        self.model = model
        self.prompt_templates = {}
        self.performance_history = []
    
    def optimize_prompt(self, task_type, current_prompt, response_quality):
        """Optimiza prompts basado en resultados previos"""
        quality_score = self._evaluate_response(response_quality)
        self.performance_history.append({
            "task": task_type,
            "prompt": current_prompt,
            "score": quality_score,
            "timestamp": time.time()
        })
        
        if quality_score < 0.7 and len(self.performance_history) > 5:
            # Generar prompt mejorado
            improvement_prompt = f"""
            Basado en esta respuesta de calidad {quality_score} para la tarea '{task_type}':
            Prompt actual: {current_prompt}
            
            Genera una versión mejorada del prompt que sea más específica, clara y efectiva.
            """
            improved = self.model.generate_content(improvement_prompt)
            return improved.text
        return current_prompt
    
    def _evaluate_response(self, response):
        """Evalúa calidad de respuesta"""
        if isinstance(response, dict):
            if response.get("success"):
                return 0.8
            return 0.3
        length_score = min(len(str(response).split()) / 100, 1.0)
        return length_score * 0.5 + 0.5  # Básico, podría mejorarse

# ============================================================
# PUNTO 8: ANALIZADOR DE ERRORES Y CORRECCIÓN
# ============================================================

class ErrorAnalyzer:
    def __init__(self):
        self.error_patterns = {}
        self.correction_strategies = {}
        
    def analyze_and_learn(self, error_type, context, successful_correction):
        """Aprende de errores y cómo corregirlos"""
        pattern_hash = hashlib.md5(f"{error_type}{context}".encode()).hexdigest()
        
        if pattern_hash not in self.error_patterns:
            self.error_patterns[pattern_hash] = {
                "type": error_type,
                "context": context,
                "occurrences": 1,
                "solutions": [successful_correction]
            }
        else:
            self.error_patterns[pattern_hash]["occurrences"] += 1
            if successful_correction not in self.error_patterns[pattern_hash]["solutions"]:
                self.error_patterns[pattern_hash]["solutions"].append(successful_correction)
        return pattern_hash
    
    def predict_and_prevent(self, current_query):
        """Predice posibles errores antes de que ocurran"""
        for pattern_hash, pattern in self.error_patterns.items():
            if pattern["occurrences"] > 3:
                if self._matches_pattern(current_query, pattern["context"]):
                    return {
                        "predicted_error": pattern["type"],
                        "suggested_solution": pattern["solutions"][0],
                        "confidence": min(pattern["occurrences"] / 10, 1.0)
                    }
        return None
    
    def _matches_pattern(self, query, context):
        """Verifica si query coincide con patrón de error conocido"""
        query_lower = query.lower()
        context_lower = context.lower()
        keywords = context_lower.split()
        matches = sum(1 for kw in keywords if kw in query_lower)
        return matches / max(len(keywords), 1) > 0.6

# ============================================================
# PUNTO 9: MOTOR DE REFLEXIÓN (Self-Reflection)
# ============================================================

class ReflectionEngine:
    def __init__(self, model, memory):
        self.model = model
        self.memory = memory
        self.reflection_log = []
    
    def reflect_on_performance(self, user_id):
        """Reflexiona sobre el rendimiento de la sesión"""
        interactions, _ = self.memory.get_all_interactions(user_id)
        
        if len(interactions) < 10:
            return "Necesito más interacciones para reflexionar significativamente."
        
        reflection_prompt = f"""
        Analiza estas {min(len(interactions), 50)} interacciones y reflexiona:
        1. ¿Qué tipo de preguntas manejé mejor?
        2. ¿Dónde fallé o di respuestas subóptimas?
        3. ¿Qué patrones de mejora identifico?
        4. ¿Qué nuevas habilidades debería desarrollar?
        
        Interacciones: {interactions[:10]}
        
        Proporciona una reflexión honesta y sugerencias concretas de mejora.
        """
        
        try:
            reflection = self.model.generate_content(reflection_prompt)
            reflection_text = reflection.text
            
            self.reflection_log.append({
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id,
                "reflection": reflection_text,
                "interactions_analyzed": len(interactions)
            })
            
            return reflection_text
        except Exception as e:
            return f"Error en reflexión: {str(e)}"
    
    def get_improvement_suggestions(self):
        """Obtiene sugerencias de mejora de reflexiones pasadas"""
        if not self.reflection_log:
            return "Sin reflexiones previas disponibles."
        
        latest = self.reflection_log[-1]["reflection"]
        suggestions = re.findall(r'(?:sugerencia|mejora|recommend|improve)[:\s]*(.+?)(?:\n|$)', 
                                 latest, re.IGNORECASE)
        return suggestions if suggestions else ["Mejorar calidad de respuestas", 
                                                "Agregar más ejemplos concretos"]

# ============================================================
# PUNTO 10: APRENDIZAJE PROACTIVO
# ============================================================

class ProactiveLearner:
    def __init__(self, knowledge_updater, memory):
        self.knowledge = knowledge_updater
        self.memory = memory
        self.topic_interest = defaultdict(int)
        
    def identify_knowledge_gaps(self, conversations):
        """Identifica temas donde el conocimiento es débil"""
        if not conversations:
            return []
        
        # Extraer temas potenciales de conversaciones
        all_text = " ".join(conversations)
        potential_topics = re.findall(r'(?:qué es|cómo funciona|explica|qué significa)\s+(.+?)(?:\?|\.)', 
                                      all_text, re.IGNORECASE)
        
        gaps = []
        for topic in potential_topics[:5]:  # Limitar a 5 temas
            self.topic_interest[topic] += 1
            if self.topic_interest[topic] > 3:  # Tema recurrente
                # Buscar información proactivamente
                new_info = self.knowledge.search_web(topic, max_results=5)
                self.knowledge.cache[topic] = new_info
                gaps.append({"topic": topic, "info_found": len(new_info)})
        
        return gaps

# ============================================================
# PUNTO 11: VALIDADOR AUTOMÁTICO
# ============================================================

class AutoValidator:
    def __init__(self, model, sandbox, math_engine):
        self.model = model
        self.sandbox = sandbox
        self.math_engine = math_engine
        self.test_results = []
        
    def validate_math_capability(self):
        """Valida capacidad matemática con casos de prueba"""
        test_cases = [
            {"input": "derivada de x^2", "expected_contains": "2*x"},
            {"input": "integral de x", "expected_contains": "x**2/2"},
            {"input": "resolver x + 2 = 5", "expected_contains": "3"}
        ]
        
        results = []
        for test in test_cases:
            result = self.math_engine.solve(test["input"])
            success = result and test["expected_contains"] in str(result)
            results.append({"test": test["input"], "passed": success, "result": result})
        
        self.test_results.append({"capability": "math", "results": results, "timestamp": time.time()})
        return results
    
    def validate_code_capability(self):
        """Valida ejecución de código"""
        if not self.sandbox.available:
            return [{"test": "code_execution", "passed": False, "error": "Sandbox no disponible"}]
        
        test_code = "print('Hello')\nresult = 2 + 2\nprint(result)"
        result = self.sandbox.execute(test_code)
        success = result["success"] and "4" in result["output"]
        
        return [{"test": "code_execution", "passed": success, "output": result.get("output")}]

# ============================================================
# PUNTO 12: ORQUESTADOR MULTIAGENTE MEJORADO
# ============================================================

class AgentOrchestrator:
    def __init__(self, memory, sandbox, knowledge, math_engine, error_analyzer):
        self.agents = {
            "code": sandbox,
            "knowledge": knowledge,
            "math": math_engine
        }
        self.memory = memory
        self.error_analyzer = error_analyzer

    def process_query(self, user_id, query):
        """Distribuye la consulta al agente adecuado"""
        # Prevenir errores conocidos
        prevention = self.error_analyzer.predict_and_prevent(query)
        if prevention and prevention["confidence"] > 0.7:
            return f"⚠️ Precaución: {prevention['predicted_error']}\nSugerencia: {prevention['suggested_solution']}"
        
        if self._is_code_query(query):
            return self._handle_code(query)
        elif self._is_math_query(query):
            return self._handle_math(query)
        elif self._is_knowledge_query(query):
            return self._handle_knowledge(query)
        else:
            return None

    def _is_code_query(self, query):
        patterns = [r'```python', r'ejecuta.*código', r'corre.*script', r'run.*code', r'execute.*python']
        return any(re.search(p, query, re.IGNORECASE) for p in patterns)

    def _is_math_query(self, query):
        patterns = [r'derivada|integral|límite|resolver.*=', r'solve|differentiate|integrate', r'\b\d+\s*[\+\-\*/]\s*\d+']
        return any(re.search(p, query, re.IGNORECASE) for p in patterns)

    def _is_knowledge_query(self, query):
        patterns = [r'últimas? noticias', r'actualizado|reciente', r'qué ha pasado', r'latest|news']
        return any(re.search(p, query, re.IGNORECASE) for p in patterns)

    def _handle_code(self, query):
        code = self._extract_code(query)
        if code:
            result = self.agents["code"].execute(code)
            if not result["success"]:
                # Aprender del error
                self.error_analyzer.analyze_and_learn("code_execution", query, 
                                                      "Verificar sintaxis y dependencias")
            return result
        return None

    def _handle_math(self, query):
        result = self.agents["math"].solve(query)
        if result is None:
            self.error_analyzer.analyze_and_learn("math_parsing", query, 
                                                  "Usar notación matemática estándar")
        return result

    def _handle_knowledge(self, query):
        return self.agents["knowledge"].get_relevant_knowledge(query)

    def _extract_code(self, text):
        match = re.search(r'```python\n?(.*?)```', text, re.DOTALL)
        return match.group(1).strip() if match else None

# ============================================================
# PUNTO 13: DASHBOARD DE AUTO-MEJORA
# ============================================================

class SelfImprovementDashboard:
    def __init__(self):
        self.metrics = {
            "accuracy": [],
            "response_time": [],
            "user_satisfaction": [],
            "learned_patterns": 0,
            "total_feedback": 0
        }
        
    def update_metrics(self, response_time, satisfaction, learned_patterns=0):
        """Actualiza métricas de rendimiento"""
        self.metrics["response_time"].append(response_time)
        self.metrics["user_satisfaction"].append(satisfaction)
        self.metrics["learned_patterns"] += learned_patterns
        
        # Mantener solo últimos 100 valores
        for key in ["response_time", "user_satisfaction"]:
            if len(self.metrics[key]) > 100:
                self.metrics[key] = self.metrics[key][-100:]
    
    def track_feedback(self, rating):
        """Registra feedback de usuario"""
        self.metrics["total_feedback"] += 1
        self.metrics["user_satisfaction"].append(rating)
    
    def get_summary(self):
        """Obtiene resumen de rendimiento"""
        avg_satisfaction = statistics.mean(self.metrics["user_satisfaction"]) if self.metrics["user_satisfaction"] else 0
        avg_response = statistics.mean(self.metrics["response_time"]) if self.metrics["response_time"] else 0
        
        return {
            "satisfaction_score": round(avg_satisfaction, 2),
            "avg_response_time": round(avg_response, 2),
            "learned_patterns": self.metrics["learned_patterns"],
            "total_feedback": self.metrics["total_feedback"],
            "trend": "📈 Mejorando" if avg_satisfaction > 3.5 else "📉 Necesita mejora"
        }
    
    def render(self):
        """Renderiza dashboard en Streamlit"""
        summary = self.get_summary()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Satisfacción", f"{summary['satisfaction_score']}/5", 
                     delta="+" if summary['satisfaction_score'] > 3 else "-")
        with col2:
            st.metric("Tiempo Respuesta", f"{summary['avg_response_time']}s")
        with col3:
            st.metric("Patrones Aprendidos", summary['learned_patterns'])
        with col4:
            st.metric("Feedback Total", summary['total_feedback'])
        
        st.caption(f"Tendencia: {summary['trend']}")

# ============================================================
# INICIALIZACIÓN DE MÓDULOS
# ============================================================

# Inicializar en sidebar
with st.sidebar:
    st.header("🔧 Módulos Activos")
    
    memory = MemorySystem()
    st.success("✅ Memoria persistente")
    
    sandbox = CodeSandbox()
    if sandbox.available:
        st.success("✅ Sandbox de código")
    else:
        st.warning("⚠️ Sandbox no disponible (Docker requerido)")
    
    knowledge = KnowledgeUpdater()
    st.success("✅ Conocimiento web")
    
    analyzer = MultimodalAnalyzer()
    st.success("✅ Análisis multimodal")
    
    math_engine = MathEngine()
    st.success("✅ Motor matemático")
    
    learning_system = LearningSystem(memory)
    st.success("✅ Sistema de aprendizaje")
    
    prompt_optimizer = PromptOptimizer(model)
    st.success("✅ Optimizador de prompts")
    
    error_analyzer = ErrorAnalyzer()
    st.success("✅ Analizador de errores")
    
    reflection_engine = ReflectionEngine(model, memory)
    st.success("✅ Motor de reflexión")
    
    proactive_learner = ProactiveLearner(knowledge, memory)
    st.success("✅ Aprendizaje proactivo")
    
    auto_validator = AutoValidator(model, sandbox, math_engine)
    st.success("✅ Validador automático")
    
    orchestrator = AgentOrchestrator(memory, sandbox, knowledge, math_engine, error_analyzer)
    st.success("✅ Orquestador multiagente")
    
    dashboard = SelfImprovementDashboard()
    st.success("✅ Dashboard de mejora")
    
    # Dashboard en sidebar
    st.header("📊 Métricas de Rendimiento")
    dashboard.render()

# ============================================================
# INTERFAZ DE CHAT PRINCIPAL
# ============================================================

# Inicializar historial
if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_id" not in st.session_state:
    st.session_state.user_id = "default_user"
if "feedback_given" not in st.session_state:
    st.session_state.feedback_given = set()

# Mostrar mensajes anteriores
for idx, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "metadata" in message:
            with st.expander("📊 Detalles técnicos"):
                st.json(message["metadata"])
        
        # Botón de feedback para mensajes del asistente
        if message["role"] == "assistant" and idx not in st.session_state.feedback_given:
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                if st.button("⭐", key=f"rating1_{idx}"):
                    learning_system.collect_feedback(st.session_state.user_id, 
                                                     st.session_state.messages[idx-1]["content"],
                                                     message["content"], 1)
                    dashboard.track_feedback(1)
                    st.session_state.feedback_given.add(idx)
                    st.rerun()
            with col2:
                if st.button("⭐⭐", key=f"rating2_{idx}"):
                    learning_system.collect_feedback(st.session_state.user_id,
                                                     st.session_state.messages[idx-1]["content"],
                                                     message["content"], 2)
                    dashboard.track_feedback(2)
                    st.session_state.feedback_given.add(idx)
                    st.rerun()
            with col3:
                if st.button("⭐⭐⭐", key=f"rating3_{idx}"):
                    learning_system.collect_feedback(st.session_state.user_id,
                                                     st.session_state.messages[idx-1]["content"],
                                                     message["content"], 3)
                    dashboard.track_feedback(3)
                    st.session_state.feedback_given.add(idx)
                    st.rerun()
            with col4:
                if st.button("⭐⭐⭐⭐", key=f"rating4_{idx}"):
                    learning_system.collect_feedback(st.session_state.user_id,
                                                     st.session_state.messages[idx-1]["content"],
                                                     message["content"], 4)
                    dashboard.track_feedback(4)
                    st.session_state.feedback_given.add(idx)
                    st.rerun()
            with col5:
                if st.button("⭐⭐⭐⭐⭐", key=f"rating5_{idx}"):
                    learning_system.collect_feedback(st.session_state.user_id,
                                                     st.session_state.messages[idx-1]["content"],
                                                     message["content"], 5)
                    dashboard.track_feedback(5)
                    st.session_state.feedback_given.add(idx)
                    st.rerun()

# Input del usuario
if prompt := st.chat_input("Escribe tu mensaje aquí (o sube una imagen)..."):

    start_time = time.time()
    
    # Mostrar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Procesar respuesta
    with st.chat_message("assistant"):
        with st.spinner("🧠 Procesando con auto-mejora..."):
            
            # 1. Verificar memoria relevante
            context = memory.recall(st.session_state.user_id, prompt)
            
            # 2. Identificar gaps de conocimiento proactivamente
            if len(st.session_state.messages) % 20 == 0:  # Cada 20 mensajes
                gaps = proactive_learner.identify_knowledge_gaps(
                    [m["content"] for m in st.session_state.messages if m["role"] == "user"]
                )
                if gaps:
                    st.info(f"📚 Aprendiendo sobre: {', '.join([g['topic'] for g in gaps])}")
            
            # 3. Intentar con agentes especializados
            agent_result = orchestrator.process_query(st.session_state.user_id, prompt)
            
            if agent_result:
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
                # 4. Usar Gemini con contexto optimizado
                enhanced_prompt = prompt
                if context:
                    enhanced_prompt = (
                        f"[Contexto de conversaciones previas]:\n"
                        f"{chr(10).join([c['text'][:200] for c in context])}\n\n"
                        f"[Consulta actual]: {prompt}"
                    )
                
                response = model.generate_content(enhanced_prompt)
                response_text = response.text
                
                # Optimizar prompt para futuras consultas similares
                prompt_optimizer.optimize_prompt("general", prompt, response_text)
            
            # Mostrar respuesta
            st.markdown(response_text)
            
            # 5. Almacenar en memoria
            metadata = {"agent_used": "gemini" if not agent_result else "specialized"}
            memory.store(st.session_state.user_id, prompt, response_text, metadata=metadata)
            
            # 6. Validación automática periódica
            if len(st.session_state.messages) % 50 == 0:  # Cada 50 mensajes
                with st.expander("🔬 Validación automática"):
                    math_results = auto_validator.validate_math_capability()
                    st.write("Resultados validación matemática:", math_results)
                    
                    if sandbox.available:
                        code_results = auto_validator.validate_code_capability()
                        st.write("Resultados validación código:", code_results)
            
            # Registrar tiempo de respuesta
            response_time = time.time() - start_time
            dashboard.update_metrics(response_time, 4)  # Default satisfaction

    # Guardar en historial
    st.session_state.messages.append({"role": "assistant", "content": response_text})

# ============================================================
# SUBIDA DE IMÁGENES
# ============================================================

with st.sidebar:
    st.header("📷 Subir imagen")
    uploaded_file = st.file_uploader("Selecciona una imagen", type=['png', 'jpg', 'jpeg'])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Imagen cargada", use_column_width=True)
        
        if st.button("🔍 Analizar imagen"):
            with st.spinner("Analizando..."):
                analysis = analyzer.analyze_image(image)
                st.json(analysis)
                
                analysis_text = f"**Análisis de imagen:**\n```json\n{json.dumps(analysis, indent=2)}\n```"
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": analysis_text,
                    "metadata": analysis
                })
                st.rerun()

# ============================================================
# CONTROLES ADICIONALES Y AUTO-MEJORA
# ============================================================

with st.sidebar:
    st.header("⚙️ Controles")
    
    if st.button("🗑️ Limpiar memoria"):
        st.session_state.messages = []
        st.session_state.feedback_given = set()
        st.rerun()
    
    if st.button("🔄 Forzar actualización de conocimiento"):
        knowledge.cache = {}
        st.success("Caché de conocimiento limpiada")
    
    if st.button("🧠 Ejecutar reflexión"):
        with st.spinner("Reflexionando..."):
            reflection = reflection_engine.reflect_on_performance(st.session_state.user_id)
            st.info(f"Reflexión completada:\n{reflection[:500]}...")
    
    if st.button("📈 Ver sugerencias de mejora"):
        suggestions = reflection_engine.get_improvement_suggestions()
        st.write("Sugerencias de mejora:")
        for s in suggestions:
            st.write(f"- {s}")
    
    user_id_input = st.text_input("ID de usuario", value=st.session_state.user_id)
    if user_id_input != st.session_state.user_id:
        st.session_state.user_id = user_id_input
        st.rerun()
    
    # Estadísticas de aprendizaje
    st.header("📚 Estadísticas de Aprendizaje")
    avg_rating = learning_system.get_average_rating(st.session_state.user_id)
    st.metric("Calificación promedio", f"{avg_rating:.2f}/5")
    st.metric("Patrones de error aprendidos", len(error_analyzer.error_patterns))
    st.metric("Topics de interés", len(proactive_learner.topic_interest))

# ============================================================
# PIE DE PÁGINA
# ============================================================

st.markdown("---")
st.caption(
    "🧠 Kai v3.0 - Asistente con Auto-Mejora Inteligente\n"
    "Características: Memoria Persistente | Ejecución de Código | Conocimiento Web | "
    "Análisis Multimodal | Motor Matemático | Feedback Learning | Auto-Prompt Optimization | "
    "Reflexión | Validación Automática | Dashboard de Rendimiento"
)
