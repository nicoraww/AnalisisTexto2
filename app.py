import streamlit as st
import pandas as pd
from textblob import TextBlob
import re
from googletrans import Translator
from streamlit_lottie import st_lottie
import json

from streamlit_lottie import st_lottie
# Configuración de la página
st.set_page_config(
    page_title="Analizador de Texto Simple",
    page_icon="📊",
    layout="wide"
)

# Cargar animación Lottie
with open('ANIMACIONTEST.json') as source:
    animation = json.load(source)
st_lottie(animation, width=350)

st.title("📝 Analizador de Texto con TextBlob")
st.markdown("""
Esta aplicación utiliza TextBlob para realizar un análisis básico de texto:
- Análisis de sentimiento y subjetividad
- Extracción de palabras clave
- Análisis de frecuencia de palabras
""")

# Sidebar
st.sidebar.title("Opciones")
modo = st.sidebar.selectbox(
    "Selecciona el modo de entrada:",
    ["Texto directo", "Archivo de texto"]
)

# Función para contar palabras
def contar_palabras(texto):
    stop_words = set([...])  # lista previa de stopwords
    palabras = re.findall(r'\b\w+\b', texto.lower())
    palabras_filtradas = [p for p in palabras if p not in stop_words and len(p) > 2]
    contador = {}
    for palabra in palabras_filtradas:
        contador[palabra] = contador.get(palabra, 0) + 1
    contador_ordenado = dict(sorted(contador.items(), key=lambda x: x[1], reverse=True))
    return contador_ordenado, palabras_filtradas

translator = Translator()

# Módulos de análisis (deben estar definidos arriba)
# from funciones_analisis import procesar_texto, crear_visualizaciones

# Área de análisis de texto directa o por archivo
if modo == "Texto directo":
    texto = st.text_area(
        label="Ingresa tu texto para analizar",
        value="",
        height=200,
        placeholder="Escribe o pega aquí el texto que deseas analizar..."
    )
    if st.button("Analizar texto"):
        if texto.strip():
            resultados = procesar_texto(texto)
            crear_visualizaciones(resultados)
        else:
            st.warning("Por favor ingresa algún texto.")
elif modo == "Archivo de texto":
    archivo = st.file_uploader(
        label="Selecciona un archivo de texto",
        type=["txt", "csv", "md"]
    )
    if archivo is not None:
        contenido = archivo.getvalue().decode("utf-8")
        if st.button("Analizar archivo"):
            resultados = procesar_texto(contenido)
            crear_visualizaciones(resultados)

# Pie de página
st.markdown("---")
st.markdown("Desarrollado con ❤️ usando Streamlit y TextBlob")
