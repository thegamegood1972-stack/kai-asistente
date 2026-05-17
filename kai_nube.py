import streamlit as st

st.set_page_config(page_title="Prueba", layout="wide")

st.title("Prueba de Kai")
st.write("Si ves esto, Streamlit funciona correctamente.")

nombre = st.text_input("Escribe tu nombre:")
if nombre:
    st.success(f"Hola {nombre}, la conexion funciona!")
