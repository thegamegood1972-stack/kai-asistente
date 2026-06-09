# ============================================================
# kai_v3_self_improving.py - Versión con Auto-Mejora Inteligente
# CORREGIDO - Memoria persistente funcionando
# Incluye configuración de secrets.toml
# ============================================================

import streamlit as st
import google.generativeai as genai
import chromadb
import docker
import cv2
import numpy as np
from sentence_transformers import SentenceTransformer
from sympy import symbols, sympify, solve, diff, integrate, simplify
from datetime import datetime
import hashlib
import json
import time
import re
from duckduckgo_search import DDGS
from PIL import Image
import statistics
from collections import defaultdict
from typing import List, Dict, Any, Optional
import os
import sys

# ============================================================
# CONFIGURACIÓN DE SECRETS (VERIFICAR)
# ============================================================

def check_secrets():
    """Verifica que los secrets estén configurados correctamente"""
    try:
        # Intentar leer desde st.secrets (Streamlit Cloud)
        if hasattr(st, 'secrets') and 'GEMINI_API_KEY' in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except:
        pass
    
    # Fallback: intentar leer desde archivo .env (desarrollo local)
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith('GEMINI_API_KEY='):
                    return line.split('=')[1].strip().strip('"').strip("'")
    
    # Si no hay API key, mostrar error
    st.error("""
    ❌ **Error: No se encontró la API Key de Gemini**
    
    ### Para solucionar:
    
    **Opción 1: Usar Streamlit Secrets (Recomendado)**
    1. Crea la carpeta `.streamlit` en el mismo directorio
    2. Crea el archivo `.streamlit/secrets.toml`
    3. Agrega: `GEMINI_API_KEY = "tu-api-key-aqui"`
    
    **Opción 2: Usar archivo .env**
    1. Crea un archivo `.env` en el mismo directorio
    2. Agrega: `GEMINI_API_KEY=tu-api-key-aqui`
    
    **Opción 3: Ingresar manualmente**
    Usa la caja de texto abajo para ingresar tu API Key.
    
    🔑 **Obtén tu API Key gratis en:** https://aistudio.google.com/
    """)
        
        # Permitir ingreso manual
        manual_key = st.text_input("🔑 Ingresa tu API Key de Gemini:", type="password")
        if manual_key:
            return manual_key
        return None
    
    return None

# Configurar Gemini
api_key = check_secrets()
if api_key:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"Error conectando con Gemini: {e}")
        st.stop()
else:
    st.stop()

# ============================================================
# CONFIGURACIÓN DE PÁGINA
# ============================================================

st.set_page_config(
    page_title="Kai - Asistente Auto-Aprendizaje",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🧠 Kai - Asistente con Auto-Mejora Inteligente (v3.0)")

# Mostrar estado de API
if api_key and api_key != "tu-api-key-aqui":
    st.sidebar.success("✅ Gemini conectado")
else:
    st.sidebar.error("⚠️ API Key no configurada")

# ============================================================
# PUNTO 1: MEMORIA PERSISTENTE (ChromaDB + Embeddings)
# ============================================================

class MemorySystem:
    def __init__(self):
        try:
            # Usar directorio persistente para ChromaDB
            persist_dir = os.path.join(os.path.dirname(__file__), ".chromadb")
            self.client = chromadb.PersistentClient(path=persist_dir)
            self.collection = self.client.get_or_create_collection("kai_memory")
            self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
            self.available = True
        except Exception as e:
            st.warning(f"⚠️ Memoria persistente no disponible: {e}")
            self.available = False

    def store(self, user_id, prompt, response, metadata=None):
        """Almacena una interacción en memoria persistente"""
        if not self.available:
            return None
            
        text = f"Usuario: {prompt}\nKai: {response}"
        embedding = self.encoder.encode(text).tolist()
        doc_id = f"{user_id}_{int(time.time())}_{hashlib.md5(text.encode()).hexdigest()[:8]}"

        meta = {
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "prompt_length": len(prompt),
            "response_length": len(response),
            **({"custom": metadata} if metadata else {})
        }

        try:
            self.collection.add(
                embeddings=[embedding],
                documents=[text],
                metadatas=[meta],
                ids=[doc_id]
            )
            return doc_id
        except Exception as e:
            print(f"Error almacenando: {e}")
            return None

    def recall(self, user_id, query, n=5):
        """Recupera interacciones relevantes del pasado"""
        if not self.available:
            return []
            
        try:
            q_emb = self.encoder.encode(query).tolist()
            results = self.collection.query(
                query_embeddings=[q_emb],
                n_results=n,
                where={"user_id": user_id}
            )

            if results['documents'] and results['documents'][0]:
                return [{
                    "text": doc,
                    "score": score,
                    "metadata": meta
                } for doc, score, meta in zip(
                    results['documents'][0],
                    results['distances'][0],
                    results['metadatas'][0]
                )]
        except Exception as e:
            print(f"Error recuperando: {e}")
        return []
    
    def get_all_interactions(self, user_id=None):
        """Recupera todas las interacciones para análisis"""
        if not self.available:
            return [], []
            
        try:
            if user_id:
                results = self.collection.get(where={"user_id": user_id})
            else:
                results = self.collection.get()
            return results.get('documents', []), results.get('metadatas', [])
        except:
            return [], []
    
    def clear_user_memory(self, user_id):
        """Limpia la memoria de un usuario específico"""
        if not self.available:
            return 0
            
        try:
            results = self.collection.get(where={"user_id": user_id})
            if results['ids']:
                self.collection.delete(ids=results['ids'])
            return len(results['ids'])
        except:
            return 0

# ============================================================
# PUNTO 2: SANDBOX DE EJECUCIÓN DE CÓDIGO
# ============================================================

class CodeSandbox:
    def __init__(self):
        self.available = False
        try:
            self.client = docker.from_env()
            self.image = "python:3.11-slim"
            self.available = True
        except:
            pass

    def execute(self, code, timeout=10):
        """Ejecuta código Python en un contenedor aislado"""
        if not self.available:
            return {"success": False, "output": "", "error": "Docker no disponible. Instala Docker para ejecutar código."}
        
        try:
            # Ejecutar código directamente sin archivos temporales
            import subprocess
            result = subprocess.run(
                ['python', '-c', code],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return {
                "success": result.returncode == 0,
                "output": result.stdout if result.returncode == 0 else result.stderr,
                "error": None if result.returncode == 0 else result.stderr
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "output": "", "error": "Tiempo de ejecución agotado"}
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
        try:
            self.face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            self.available = True
        except:
            self.available = False

    def analyze_image(self, image):
        """Analiza una imagen y extrae información técnica"""
        if not self.available:
            return {"error": "OpenCV no disponible"}
            
        try:
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
        except Exception as e:
            return {"error": str(e)}

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
            'derivative': r'(derivada|diferenciar|derive)\s+(?:de\s+)?(.+?)(?:\s+respecto\s+a\s+(\w))?$',
            'integral': r'(integral|integrar|integrate)\s+(.+?)(?:\s+respecto\s+a\s+(\w))?$',
            'solve': r'(resolver|solucionar|solve)\s+(.+?)(?:\s+para\s+(\w))?$',
            'simplify': r'(simplificar|simplify)\s+(.+?)$',
            'limit': r'(límite|limite|limit)\s+de\s+(.+?)(?:\s+cuando\s+(\w)\s*->\s*([\d.]+))?$'
        }
        for op, pattern in patterns.items():
            match = re.match(pattern, query, re.IGNORECASE)
            if match:
                groups = match.groups()
                try:
                    if op in ['derivative', 'integral']:
                        expr = groups[1].strip()
                        var = groups[2] if groups[2] else 'x'
                        return self.operators[op](expr, var)
                    elif op == 'solve':
                        expr = groups[1].strip()
                        var = groups[2] if groups[2] else 'x'
                        return self.operators[op](expr, var)
                    elif op == 'simplify':
                        return self.operators[op](groups[1].strip())
                    elif op == 'limit':
                        expr = groups[1].strip()
                        var = groups[2] if groups[2] else 'x'
                        point = float(groups[3]) if groups[3] else 0
                        return self.operators[op](expr, var, point)
                except Exception as e:
                    return f"Error matemático: {str(e)}"
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
            "response": response[:500],
            "rating": user_rating,
            "timestamp": datetime.now().isoformat()
        }
        self.feedback_log.append(feedback_entry)
        self.performance_metrics[user_id].append(user_rating)
        
        if user_rating < 3:
            self._improve_response_pattern(prompt, response)
        
        if self.memory:
            self.memory.store(user_id, prompt, response, 
                             metadata={"feedback": user_rating, "type": "user_feedback"})
        return True
    
    def _improve_response_pattern(self, bad_prompt, bad_response):
        """Analiza respuestas malas para mejorar"""
        patterns = {
            "too_vague": len(bad_response.split()) < 20,
            "too_long": len(bad_response.split()) > 500,
            "off_topic": self._check_relevance(bad_prompt, bad_response),
        }
        if self.memory:
            pattern_key = hashlib.md5(bad_prompt.encode()).hexdigest()
            self.memory.store("learning_system", bad_prompt, bad_response, 
                             metadata={"failed": True, "patterns": patterns, "pattern_key": pattern_key})
    
    def _check_relevance(self, prompt, response):
        prompt_words = set(prompt.lower().split())
        response_words = set(response.lower().split())
        overlap = len(prompt_words & response_words) / max(len(prompt_words), 1)
        return overlap < 0.2
    
    def get_average_rating(self, user_id=None):
        if user_id and user_id in self.performance_metrics:
            ratings = self.performance_metrics[user_id]
            return statistics.mean(ratings) if ratings else 0
        all_ratings = [r for ratings in self.performance_metrics.values() for r in ratings]
        return statistics.mean(all_ratings) if all_ratings else 0

# ============================================================
# PUNTO 7: OPTIMIZADOR DE PROMPTS
# ============================================================

class PromptOptimizer:
    def __init__(self, model):
        self.model = model
        self.prompt_history = []
    
    def optimize_prompt(self, task_type, current_prompt, response_quality):
        quality_score = self._evaluate_response(response_quality)
        self.prompt_history.append({
            "task": task_type,
            "prompt": current_prompt[:200],
            "score": quality_score,
            "timestamp": time.time()
        })
        
        if len(self.prompt_history) > 50:
            self.prompt_history = self.prompt_history[-50:]
        
        if quality_score < 0.6 and len(self.prompt_history) > 5:
            improvement_prompt = f"""
            Analiza esta respuesta de calidad baja ({quality_score}) para la tarea '{task_type}':
            Prompt original: {current_prompt[:300]}
            
            Genera UNA SOLA sugerencia específica para mejorar este prompt.
            """
            try:
                improved = self.model.generate_content(improvement_prompt)
                return improved.text[:500]
            except:
                pass
        return None
    
    def _evaluate_response(self, response):
        if isinstance(response, dict):
            if response.get("success"):
                return 0.8
            return 0.3
        if isinstance(response, list):
            return 0.7 if response else 0.3
        response_str = str(response)
        length_score = min(len(response_str.split()) / 150, 1.0)
        return length_score * 0.6 + 0.4

# ============================================================
# PUNTO 8: ANALIZADOR DE ERRORES Y CORRECCIÓN
# ============================================================

class ErrorAnalyzer:
    def __init__(self):
        self.error_patterns = {}
        
    def analyze_and_learn(self, error_type, context, successful_correction):
        pattern_hash = hashlib.md5(f"{error_type}{context[:100]}".encode()).hexdigest()
        
        if pattern_hash not in self.error_patterns:
            self.error_patterns[pattern_hash] = {
                "type": error_type,
                "context": context[:200],
                "occurrences": 1,
                "solutions": [successful_correction]
            }
        else:
            self.error_patterns[pattern_hash]["occurrences"] += 1
            if successful_correction not in self.error_patterns[pattern_hash]["solutions"]:
                self.error_patterns[pattern_hash]["solutions"].append(successful_correction)
        return pattern_hash
    
    def predict_and_prevent(self, current_query):
        for pattern in self.error_patterns.values():
            if pattern["occurrences"] > 3:
                if self._matches_pattern(current_query, pattern["context"]):
                    return {
                        "predicted_error": pattern["type"],
                        "suggested_solution": pattern["solutions"][0],
                        "confidence": min(pattern["occurrences"] / 10, 1.0)
                    }
        return None
    
    def _matches_pattern(self, query, context):
        query_lower = query.lower()
        context_lower = context.lower()
        keywords = context_lower.split()
        matches = sum(1 for kw in keywords if kw in query_lower)
        return matches / max(len(keywords), 1) > 0.5

# ============================================================
# PUNTO 9: MOTOR DE REFLEXIÓN
# ============================================================

class ReflectionEngine:
    def __init__(self, model, memory):
        self.model = model
        self.memory = memory
        self.reflection_log = []
    
    def reflect_on_performance(self, user_id):
        if not self.memory:
            return "Memoria no disponible para reflexionar."
            
        interactions, _ = self.memory.get_all_interactions(user_id)
        
        if len(interactions) < 5:
            return "Necesito al menos 5 interacciones para reflexionar significativamente."
        
        reflection_prompt = f"""
        Basado en estas {min(len(interactions), 20)} interacciones recientes, haz una breve reflexión:
        
        Interacciones: {interactions[-5:]}
        
        Responde SOLO estas 3 preguntas en español:
        1. ¿Qué tipo de preguntas respondí mejor?
        2. ¿Qué fallo común detecto?
        3. ¿Una sugerencia concreta de mejora?
        """
        
        try:
            reflection = self.model.generate_content(reflection_prompt)
            reflection_text = reflection.text
            
            self.reflection_log.append({
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id,
                "reflection": reflection_text[:500],
                "interactions_analyzed": len(interactions)
            })
            
            return reflection_text
        except Exception as e:
            return f"Error en reflexión: {str(e)}"
    
    def get_improvement_suggestions(self):
        if not self.reflection_log:
            return ["Realizar más interacciones para generar sugerencias"]
        
        latest = self.reflection_log[-1]["reflection"]
        suggestions = re.findall(r'(?:sugerencia|mejora|recommend|improve)[:\s]*(.+?)(?:\n|\.)', 
                                 latest, re.IGNORECASE)
        return suggestions[:3] if suggestions else ["Mejorar calidad de respuestas"]

# ============================================================
# PUNTO 10: APRENDIZAJE PROACTIVO
# ============================================================

class ProactiveLearner:
    def __init__(self, knowledge_updater, memory):
        self.knowledge = knowledge_updater
        self.memory = memory
        self.topic_interest = defaultdict(int)
        self.learned_topics = set()
        
    def identify_knowledge_gaps(self, conversations):
        if not conversations:
            return []
        
        all_text = " ".join(conversations[-10:])
        topic_patterns = [
            r'(?:qué es|qué son|explica|cómo funciona)\s+([a-záéíóúñ\s]{3,30}?)(?=\?|\.|$)',
            r'(?:dime sobre|habla de|cuéntame de)\s+([a-záéíóúñ\s]{3,30}?)(?=\?|\.|$)'
        ]
        
        potential_topics = []
        for pattern in topic_patterns:
            matches = re.findall(pattern, all_text, re.IGNORECASE)
            potential_topics.extend(matches)
        
        gaps = []
        for topic in potential_topics[:3]:
            if topic not in self.learned_topics:
                self.topic_interest[topic] += 1
                if self.topic_interest[topic] >= 2:
                    new_info = self.knowledge.search_web(topic, max_results=2)
                    self.knowledge.cache[topic] = new_info
                    self.learned_topics.add(topic)
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
        test_cases = [
            {"input": "derivada de x^2", "expected_contains": "2*x", "name": "derivada simple"},
            {"input": "derivada de x^3", "expected_contains": "3*x**2", "name": "derivada x^3"},
            {"input": "integral de x", "expected_contains": "x**2/2", "name": "integral simple"}
        ]
        
        results = []
        for test in test_cases:
            result = self.math_engine.solve(test["input"])
            success = result and test["expected_contains"].replace("*", "").replace(" ", "") in str(result).replace("*", "").replace(" ", "")
            results.append({"test": test["name"], "passed": success, "result": str(result)[:100]})
        
        self.test_results.append({"capability": "math", "results": results, "timestamp": time.time()})
        return results
    
    def validate_code_capability(self):
        if not self.sandbox.available:
            return [{"test": "code_execution", "passed": False, "error": "Sandbox no disponible"}]
        
        test_code = "print(2 + 2)"
        result = self.sandbox.execute(test_code)
        success = result["success"] and "4" in result["output"]
        
        return [{"test": "code_execution", "passed": success, "output": result.get("output", "")[:100]}]

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
        prevention = self.error_analyzer.predict_and_prevent(query)
        if prevention and prevention["confidence"] > 0.8:
            return f"⚠️ Precaución: {prevention['predicted_error']}\n💡 Sugerencia: {prevention['suggested_solution']}"
        
        if self._is_code_query(query):
            return self._handle_code(query)
        elif self._is_math_query(query):
            return self._handle_math(query)
        elif self._is_knowledge_query(query):
            return self._handle_knowledge(query)
        else:
            return None

    def _is_code_query(self, query):
        patterns = [r'```python', r'ejecuta.*código', r'corre.*script', r'run.*code', r'execute.*python', r'```\s*\n']
        return any(re.search(p, query, re.IGNORECASE) for p in patterns)

    def _is_math_query(self, query):
        patterns = [r'derivada|integral|límite|resolver', r'solve|differentiate|integrate', r'd/dx|∫']
        return any(re.search(p, query, re.IGNORECASE) for p in patterns)

    def _is_knowledge_query(self, query):
        patterns = [r'últimas? noticias', r'actualizado|reciente', r'qué ha pasado', r'latest|news', r'hoy en']
        return any(re.search(p, query, re.IGNORECASE) for p in patterns)

    def _handle_code(self, query):
        code = self._extract_code(query)
        if code:
            result = self.agents["code"].execute(code)
            if not result["success"]:
                self.error_analyzer.analyze_and_learn("code_execution", query[:200], 
                                                      "Verificar sintaxis y usar print() para ver resultados")
            return result
        return None

    def _handle_math(self, query):
        result = self.agents["math"].solve(query)
        if result is None:
            self.error_analyzer.analyze_and_learn("math_parsing", query[:200], 
                                                  "Usar notación como: derivada de x^2, integral de x, resolver x+2=5")
            return None
        return result

    def _handle_knowledge(self, query):
        return self.agents["knowledge"].get_relevant_knowledge(query)

    def _extract_code(self, text):
        match = re.search(r'```python\n?(.*?)```', text, re.DOTALL)
        if match:
            return match.group(1).strip()
        lines = text.split('\n')
        if any('def ' in line or 'import ' in line or 'print(' in line for line in lines):
            return text
        return None

# ============================================================
# PUNTO 13: DASHBOARD DE AUTO-MEJORA
# ============================================================

class SelfImprovementDashboard:
    def __init__(self):
        self.metrics = {
            "response_times": [],
            "user_satisfaction": [],
            "learned_patterns": 0,
            "total_feedback": 0
        }
        
    def update_metrics(self, response_time, satisfaction=0):
        self.metrics["response_times"].append(response_time)
        if satisfaction > 0:
            self.metrics["user_satisfaction"].append(satisfaction)
        
        if len(self.metrics["response_times"]) > 100:
            self.metrics["response_times"] = self.metrics["response_times"][-100:]
        if len(self.metrics["user_satisfaction"]) > 100:
            self.metrics["user_satisfaction"] = self.metrics["user_satisfaction"][-100:]
    
    def track_feedback(self, rating):
        self.metrics["total_feedback"] += 1
        self.metrics["user_satisfaction"].append(rating)
    
    def get_summary(self):
        avg_satisfaction = statistics.mean(self.metrics["user_satisfaction"]) if self.metrics["user_satisfaction"] else 0
        avg_response = statistics.mean(self.metrics["response_times"]) if self.metrics["response_times"] else 0
        
        return {
            "satisfaction_score": round(avg_satisfaction, 2),
            "avg_response_time": round(avg_response, 2),
            "learned_patterns": self.metrics["learned_patterns"],
            "total_feedback": self.metrics["total_feedback"],
            "trend": "📈 Mejorando" if avg_satisfaction > 3.5 else "📉 Necesita mejora"
        }
    
    def render(self):
        summary = self.get_summary()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Satisfacción", f"{summary['satisfaction_score']}/5", 
                     delta="📈" if summary['satisfaction_score'] > 3 else "📉")
        with col2:
            st.metric("Tiempo Respuesta", f"{summary['avg_response_time']:.1f}s")
        with col3:
            st.metric("Patrones Aprendidos", summary['learned_patterns'])
        with col4:
            st.metric("Feedback Total", summary['total_feedback'])
        
        if summary['total_feedback'] > 0:
            st.caption(f"Tendencia: {summary['trend']}")

# ============================================================
# INICIALIZACIÓN DE MÓDULOS
# ============================================================

@st.cache_resource
def init_modules():
    """Inicializa todos los módulos (cacheado para rendimiento)"""
    memory = MemorySystem()
    sandbox = CodeSandbox()
    knowledge = KnowledgeUpdater()
    analyzer = MultimodalAnalyzer()
    math_engine = MathEngine()
    learning_system = LearningSystem(memory)
    prompt_optimizer = PromptOptimizer(model)
    error_analyzer = ErrorAnalyzer()
    reflection_engine = ReflectionEngine(model, memory)
    proactive_learner = ProactiveLearner(knowledge, memory)
    auto_validator = AutoValidator(model, sandbox, math_engine)
    orchestrator = AgentOrchestrator(memory, sandbox, knowledge, math_engine, error_analyzer)
    dashboard = SelfImprovementDashboard()
    
    return {
        "memory": memory,
        "sandbox": sandbox,
        "knowledge": knowledge,
        "analyzer": analyzer,
        "math_engine": math_engine,
        "learning_system": learning_system,
        "prompt_optimizer": prompt_optimizer,
        "error_analyzer": error_analyzer,
        "reflection_engine": reflection_engine,
        "proactive_learner": proactive_learner,
        "auto_validator": auto_validator,
        "orchestrator": orchestrator,
        "dashboard": dashboard
    }

# Inicializar módulos
modules = init_modules()

# Mostrar estado en sidebar
with st.sidebar:
    st.header("🔧 Módulos Activos")
    
    if modules["memory"].available:
        st.success("✅ Memoria persistente")
    else:
        st.warning("⚠️ Memoria no disponible")
    
    if modules["sandbox"].available:
        st.success("✅ Sandbox de código")
    else:
        st.info("📦 Docker no instalado - Código limitado")
    
    st.success("✅ Conocimiento web")
    
    if modules["analyzer"].available:
        st.success("✅ Análisis multimodal")
    else:
        st.warning("⚠️ Análisis de imágenes no disponible")
    
    st.success("✅ Motor matemático")
    st.success("✅ Sistema de aprendizaje")
    st.success("✅ Orquestador multiagente")

# ============================================================
# INTERFAZ DE CHAT PRINCIPAL
# ============================================================

# Inicializar estado de sesión
if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_id" not in st.session_state:
    st.session_state.user_id = "default_user"
if "feedback_given" not in st.session_state:
    st.session_state.feedback_given = set()
if "validation_done" not in st.session_state:
    st.session_state.validation_done = False

# Mostrar mensajes anteriores
for idx, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Botones de feedback para mensajes del asistente
        if message["role"] == "assistant" and idx not in st.session_state.feedback_given and idx > 0:
            st.caption("📊 ¿Qué te pareció esta respuesta?")
            cols = st.columns(5)
            ratings = [("⭐ 1", 1), ("⭐⭐ 2", 2), ("⭐⭐⭐ 3", 3), ("⭐⭐⭐⭐ 4", 4), ("⭐⭐⭐⭐⭐ 5", 5)]
            
            for col, (label, rating) in zip(cols, ratings):
                with col:
                    if st.button(label, key=f"rate_{idx}_{rating}"):
                        modules["learning_system"].collect_feedback(
                            st.session_state.user_id,
                            st.session_state.messages[idx-1]["content"],
                            message["content"], rating)
                        modules["dashboard"].track_feedback(rating)
                        st.session_state.feedback_given.add(idx)
                        st.rerun()

# Input del usuario
if prompt := st.chat_input("Escribe tu mensaje aquí..."):

    start_time = time.time()
    
    # Mostrar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Procesar respuesta
    with st.chat_message("assistant"):
        with st.spinner("🧠 Procesando con auto-mejora..."):
            
            # 1. RECUPERAR MEMORIA
            context = modules["memory"].recall(st.session_state.user_id, prompt, n=5)
            
            if context:
                st.sidebar.info(f"📖 Memoria: {len(context)} items recuperados")
            
            # 2. Identificar gaps de conocimiento
            if len(st.session_state.messages) % 15 == 0 and len(st.session_state.messages) > 5:
                gaps = modules["proactive_learner"].identify_knowledge_gaps(
                    [m["content"] for m in st.session_state.messages if m["role"] == "user"]
                )
                if gaps:
                    st.info(f"📚 Aprendiendo sobre: {', '.join([g['topic'] for g in gaps[:2]])}")
            
            # 3. Intentar con agentes especializados
            agent_result = modules["orchestrator"].process_query(st.session_state.user_id, prompt)
            
            if agent_result:
                if isinstance(agent_result, dict):
                    if agent_result.get("success"):
                        response_text = f"**💻 Ejecución de código:**\n```\n{agent_result['output']}\n```"
                    else:
                        response_text = f"❌ Error: {agent_result.get('error', 'Desconocido')}"
                elif isinstance(agent_result, list):
                    response_text = "**🔍 Resultados de búsqueda:**\n\n"
                    for r in agent_result[:2]:
                        response_text += f"**{r.get('title', 'Resultado')}**\n{r.get('body', str(r))[:300]}\n\n"
                else:
                    response_text = f"**🧮 Resultado matemático:**\n```\n{str(agent_result)}\n```"
            else:
                # 4. Usar Gemini con contexto
                if context:
                    context_text = []
                    for c in context[:3]:
                        text = c['text'][:400]
                        context_text.append(text)
                    
                    enhanced_prompt = f"""INSTRUCCIÓN: Usa el siguiente contexto de conversaciones anteriores.

CONTEXTO PREVIO:
{chr(10).join(['- ' + t for t in context_text])}

CONSULTA ACTUAL: {prompt}

Responde de manera natural y útil."""
                else:
                    enhanced_prompt = prompt
                
                try:
                    response = model.generate_content(enhanced_prompt)
                    response_text = response.text
                except Exception as e:
                    response_text = f"Error: {str(e)}"
            
            st.markdown(response_text)
            
            # 5. Almacenar en memoria
            modules["memory"].store(st.session_state.user_id, prompt, response_text[:1000])
            
            # 6. Validación automática
            if len(st.session_state.messages) >= 20 and not st.session_state.validation_done:
                with st.expander("🔬 Validación automática"):
                    math_results = modules["auto_validator"].validate_math_capability()
                    st.write("✅ Matemáticas:", math_results)
                    if modules["sandbox"].available:
                        code_results = modules["auto_validator"].validate_code_capability()
                        st.write("✅ Código:", code_results)
                    modules["dashboard"].metrics["learned_patterns"] += 1
                    st.session_state.validation_done = True
            
            # Registrar tiempo
            response_time = time.time() - start_time
            modules["dashboard"].update_metrics(response_time)
            st.sidebar.caption(f"⏱️ Respuesta: {response_time:.1f}s")

    st.session_state.messages.append({"role": "assistant", "content": response_text})
    st.rerun()

# ============================================================
# SIDEBAR - CONTROLES Y ESTADÍSTICAS
# ============================================================

with st.sidebar:
    st.header("📊 Dashboard")
    modules["dashboard"].render()
    
    st.header("⚙️ Controles")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Limpiar chat"):
            st.session_state.messages = []
            st.session_state.feedback_given = set()
            st.rerun()
    
    with col2:
        if st.button("🔄 Reset validación"):
            st.session_state.validation_done = False
            st.success("Validación reiniciada")
    
    if st.button("🧠 Reflexionar"):
        with st.spinner("Reflexionando..."):
            reflection = modules["reflection_engine"].reflect_on_performance(st.session_state.user_id)
            st.info(f"🧠 {reflection[:400]}...")
    
    if st.button("📈 Sugerencias"):
        suggestions = modules["reflection_engine"].get_improvement_suggestions()
        for s in suggestions:
            st.write(f"💡 {s}")
    
    if st.button("🔍 Probar memoria"):
        test_prompt = "¿Recuerdas algo sobre mí?"
        context = modules["memory"].recall(st.session_state.user_id, test_prompt, n=3)
        if context:
            st.success(f"✅ {len(context)} items en memoria")
        else:
            st.info("📝 Sin memoria aún. Interactúa más.")
    
    st.header("📚 Estadísticas")
    avg_rating = modules["learning_system"].get_average_rating(st.session_state.user_id)
    st.metric("Calificación", f"{avg_rating:.2f}/5" if avg_rating > 0 else "Sin datos")
    st.metric("Patrones error", len(modules["error_analyzer"].error_patterns))
    st.metric("Tópicos aprendidos", len(modules["proactive_learner"].learned_topics))
    
    st.header("👤 Usuario")
    new_user_id = st.text_input("ID", value=st.session_state.user_id)
    if new_user_id != st.session_state.user_id:
        st.session_state.user_id = new_user_id
        st.rerun()

# ============================================================
# SUBIDA DE IMÁGENES
# ============================================================

with st.sidebar:
    st.header("📷 Análisis de Imagen")
    uploaded_file = st.file_uploader("Sube una imagen", type=['png', 'jpg', 'jpeg'])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Imagen", use_column_width=True)
        
        if st.button("🔍 Analizar"):
            with st.spinner("Analizando..."):
                analysis = modules["analyzer"].analyze_image(image)
                if "error" not in analysis:
                    st.json(analysis)
                    analysis_text = f"**📸 Análisis:**\n```json\n{json.dumps(analysis, indent=2)}\n```"
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": analysis_text
                    })
                    st.rerun()
                else:
                    st.error(f"Error: {analysis['error']}")

# ============================================================
# PIE DE PÁGINA
# ============================================================

st.markdown("---")
st.caption(
    "🧠 **Kai v3.0** | Memoria persistente | Ejecución código | "
    "Matemáticas | Feedback | Reflexión | Validación automática\n"
    "💡 **Tips:** Califica con ⭐ | Usa 'derivada de...' | Sube imágenes | Código entre ```python"
)
