import streamlit as st
import pandas as pd
from textblob import TextBlob
import re
from googletrans import Translator
from streamlit_lottie import st_lottie
import json
import time

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
    stop_words = set([
        # regiones truncadas para brevedad; incluir lista completa de stopwords
        'a','al','algo','algunas','algunos','ante','antes','como','con','contra',
        'cual','cuando','de','del','desde','donde','durante','e','el','ella',
        'ellas','ellos','en','entre','era','eras','es','esa','esas','ese',
        # ... continuar lista en español e inglés
    ])
    palabras = re.findall(r"\b\w+\b", texto.lower())
    filtradas = [p for p in palabras if p not in stop_words and len(p) > 2]
    contador = {}
    for p in filtradas:
        contador[p] = contador.get(p, 0) + 1
    contador_ordenado = dict(sorted(contador.items(), key=lambda x: x[1], reverse=True))
    return contador_ordenado, filtradas

translator = Translator()

# Función de traducción al inglés
def traducir_texto(texto):
    try:
        return translator.translate(texto, src='es', dest='en').text
    except:
        return texto

# Función principal de procesamiento de texto
def procesar_texto(texto):
    texto_original = texto
    texto_ingles = traducir_texto(texto)
    blob = TextBlob(texto_ingles)
    sentimiento = blob.sentiment.polarity
    subjetividad = blob.sentiment.subjectivity
    # Frases originales y traducidas
    frases_o = [f.strip() for f in re.split(r'[.!?]+', texto_original) if f.strip()]
    frases_t = [f.strip() for f in re.split(r'[.!?]+', texto_ingles) if f.strip()]
    combinadas = []
    for i in range(min(len(frases_o), len(frases_t))):
        combinadas.append({'original': frases_o[i], 'traducido': frases_t[i]})
    contador_pal, palabras = contar_palabras(texto_ingles)
    return {
        'sentimiento': sentimiento,
        'subjetividad': subjetividad,
        'frases': combinadas,
        'contador_palabras': contador_pal,
        'palabras': palabras,
        'texto_original': texto_original,
        'texto_traducido': texto_ingles
    }

# Función para visualizaciones
def crear_visualizaciones(res):
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Sentimiento y Subjetividad")
        sent_norm = (res['sentimiento'] + 1) / 2
        st.write("**Sentimiento:**")
        st.progress(sent_norm)
        if res['sentimiento'] > 0.05:
            st.success(f"Positivo ({res['sentimiento']:.2f})")
        elif res['sentimiento'] < -0.05:
            st.error(f"Negativo ({res['sentimiento']:.2f})")
        else:
            st.info(f"Neutral ({res['sentimiento']:.2f})")
        st.write("**Subjetividad:**")
        st.progress(res['subjetividad'])
        if res['subjetividad'] > 0.5:
            st.warning(f"Alta subjetividad ({res['subjetividad']:.2f})")
        else:
            st.info(f"Baja subjetividad ({res['subjetividad']:.2f})")
    with col2:
        st.subheader("Palabras frecuentes")
        top = dict(list(res['contador_palabras'].items())[:10])
        st.bar_chart(top)

    # Conteo de Prefijos
    st.subheader("Conteo de Prefijos")
    prefixes = ['a', 'ante', 'para', 'por', 'contar', 'desde']
    text_lower = res['texto_original'].lower()
    prefix_counts = {p: len(re.findall(rf"{p}", text_lower)) for p in prefixes}
    st.bar_chart(prefix_counts)

    st.subheader("Texto traducido")
    with st.expander("Ver traducción completa"):
        st.write("**Original:**")
        st.text(res['texto_original'])
        st.write("**Traducido:**")
        st.text(res['texto_traducido'])
    st.subheader("Frases detectadas")
    for i, f in enumerate(res['frases'][:10], 1):
        try:
            blob_f = TextBlob(f['traducido'])
            emo = '😊' if blob_f.sentiment.polarity > 0.05 else ('😟' if blob_f.sentiment.polarity < -0.05 else '😐')
        except:
            emo = ''
        st.write(f"{i}. {emo} **Original:** {f['original']}")
        st.write(f"   Traducción: {f['traducido']}")
        st.write('---')

# Lógica principal
# Iniciar contador de tiempo para medir velocidad de escritura
if "typing_start" not in st.session_state:
    st.session_state.typing_start = time.time()

if modo == "Texto directo":
    texto = st.text_area(
        label="Ingresa tu texto para analizar",
        value="",
        height=200,
        placeholder="Escribe o pega aquí el texto..."
    )
    if st.button("Analizar texto"):
        if texto.strip():
            # Calcular velocidad de escritura
            elapsed = time.time() - st.session_state.typing_start
            words = len(texto.split())
            wpm = (words / elapsed) * 60 if elapsed > 0 else 0
            # Procesar y visualizar
            res = procesar_texto(texto)
            crear_visualizaciones(res)
            # Mostrar velocidad
            st.info(f"💨 Velocidad de escritura: {wpm:.2f} palabras por minuto")
        else:
            st.warning("Por favor ingresa algún texto.")
elif modo == "Archivo de texto":
    archivo = st.file_uploader(
        label="Selecciona un archivo",
        type=["txt","csv","md"]
    )
    if archivo:
        cont = archivo.getvalue().decode('utf-8')
        if st.button("Analizar archivo"):
            res = procesar_texto(cont)
            crear_visualizaciones(res)

if modo == "Texto directo":
    texto = st.text_area(
        label="Ingresa tu texto para analizar",
        value="",
        height=200,
        placeholder="Escribe o pega aquí el texto..."
    )
    if st.button("Analizar texto"):
        if texto.strip():
            res = procesar_texto(texto)
            crear_visualizaciones(res)
        else:
            st.warning("Por favor ingresa algún texto.")
elif modo == "Archivo de texto":
    archivo = st.file_uploader(
        label="Selecciona un archivo",
        type=["txt","csv","md"]
    )
    if archivo:
        cont = archivo.getvalue().decode('utf-8')
        if st.button("Analizar archivo"):
            res = procesar_texto(cont)
            crear_visualizaciones(res)

# Pie de página
st.markdown("---")
st.markdown("Desarrollado con ❤️ usando Streamlit y TextBlob")
