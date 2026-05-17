# kai_nube.py - Entiende preguntas complejas
import streamlit as st
import requests

st.set_page_config(page_title="Kai - Asistente IA", layout="wide")

st.title("🌊 Kai - Asistente de IA")
st.markdown("Entiendo preguntas como: *¿puedes darme la formula de sistema no lineal?*")

# ========== BASE DE CONOCIMIENTO ==========
def dar_codigo_generico(tema):
    tema_lower = tema.lower()
    if "saludo" in tema_lower or "hola" in tema_lower:
        return """**Codigo Python - Saludo simple**

```python
nombre = input("¿Como te llamas? ")
print(f"¡Hola {nombre}! Bienvenido a Python")
```"""
    return dar_codigo_red_neuronal()

def dar_codigo_red_neuronal():
    return """**Codigo Python - Red Neuronal Simple**

```python
import numpy as np

class RedNeuronal:
    def __init__(self, entradas, salidas):
        self.pesos = np.random.randn(entradas, salidas) * 0.1
    def activacion(self, x):
        return 1 / (1 + np.exp(-x))
    def predecir(self, entrada):
        return self.activacion(np.dot(entrada, self.pesos))

nn = RedNeuronal(2, 1)
print(f"Prediccion: {nn.predecir([0.5, 0.8])}")
```"""

# ========== FORMULAS MATEMATICAS ==========
def dar_formula_sistema_no_lineal():
    return """**Sistemas No Lineales - Concepto y Ejemplo**

No existe una **formula unica** para sistemas no lineales, ya que cada sistema se describe con ecuaciones especificas.

**Ejemplo de ecuacion no lineal:**
