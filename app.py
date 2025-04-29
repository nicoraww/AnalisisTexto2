import streamlit as st
from textblob import TextBlob
import re
from googletrans import Translator
from streamlit_lottie import st_lottie
import json
import time
import pandas as pd

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

# Título y descripción
st.title("📝 Analizador de Texto con TextBlob")
st.markdown("""
Esta aplicación utiliza TextBlob para realizar un análisis básico de texto:
- Análisis de sentimiento y subjetividad
- Extracción de palabras clave
- Análisis de frecuencia de palabras
- Cálculo de velocidad de escritura
- Conteo de preposiciones seleccionadas
""")

# Sidebar: modo de entrada
st.sidebar.title("Opciones")
modo = st.sidebar.selectbox(
    "Selecciona el modo de entrada:",
    ["Texto directo", "Archivo de texto"],
    key="input_mode"
)

# Función para contar palabras (stopwords básicas)
def contar_palabras(texto):
    stop_words = set([
        'a','al','algo','algunas','algunos','ante','antes','como','con','contra',
        'cual','cuando','de','del','desde','donde','durante','e','el','ella',
        'ellas','ellos','en','entre','era','eras','es','esa','esas','ese','eso','esos',
        'esta','estas','este','esto','estos','ha','había','han','has','hasta','he',
        'la','las','le','les','lo','los','me','mi','mía','mías','mío','míos','mis','mucho',
        'muchos','muy','nada','ni','no','nos','nosotras','nosotros','nuestra','nuestras',
        'nuestro','nuestros','o','os','otra','otras','otro','otros','para','pero','poco',
        'por','porque','que','quien','quienes','qué','se','sea','sean','según','sin','so',
        'sobre','sois','somos','son','soy','su','sus','suya','suyas','suyo','suyos','también',
        'tanto','te','tenéis','tenemos','tener','tengo','ti','tiene','tienen','todo','todos',
        'tu','tus','tuya','tuyas','tuyo','tuyos','tú','un','una','uno','unos','vosotras',
        'vosotros','vuestra','vuestras','vuestro','vuestros','y','ya','yo'
    ])
    palabras = re.findall(r"\b\w+\b", texto.lower())
    filtradas = [p for p in palabras if p not in stop_words and len(p) > 2]
    contador = {}
    for p in filtradas:
        contador[p] = contador.get(p, 0) + 1
    return dict(sorted(contador.items(), key=lambda x: x[1], reverse=True)), filtradas

translator = Translator()

def traducir_texto(texto):
    try:
        return translator.translate(texto, src='es', dest='en').text
    except:
        return texto

# Procesamiento de texto principal
def procesar_texto(texto):
    texto_original = texto
    texto_ingles = traducir_texto(texto)
    blob = TextBlob(texto_ingles)
    sentimiento = blob.sentiment.polarity
    subjetividad = blob.sentiment.subjectivity
    frases_o = [f.strip() for f in re.split(r'[.!?]+', texto_original) if f.strip()]
    frases_t = [f.strip() for f in re.split(r'[.!?]+', texto_ingles) if f.strip()]
    combinadas = [
        {'original': frases_o[i], 'traducido': frases_t[i]}
        for i in range(min(len(frases_o), len(frases_t)))
    ]
    contador_palabras, palabras = contar_palabras(texto_ingles)
    return {
        'sentimiento': sentimiento,
        'subjetividad': subjetividad,
        'frases': combinadas,
        'contador_palabras': contador_palabras,
        'palabras': palabras,
        'texto_original': texto_original,
        'texto_traducido': texto_ingles
    }

# Función de visualizaciones
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
        st.subheader("Palabras más frecuentes")
        top = dict(list(res['contador_palabras'].items())[:10])
        st.bar_chart(top)
    # Conteo de Preposiciones
    st.subheader("Conteo de Preposiciones")
    preposiciones = [
        'a','ante','bajo','cabe','con','contra','de','desde','durante','en','entre',
        'hacia','hasta','mediante','para','por','según','sin','so','sobre','tras',
        'versus','vía'
    ]
    text_lower = res['texto_original'].lower()
    prep_counts = {
        p: len(re.findall(rf"\b{re.escape(p)}\b", text_lower))
        for p in preposiciones
    }
    st.bar_chart(prep_counts)
    # Texto traducido
    st.subheader("Texto Traducido")
    with st.expander("Ver traducción completa"):
        st.write("**Original:**", res['texto_original'])
        st.write("**Traducido:**", res['texto_traducido'])
    # Frases detectadas
    st.subheader("Frases detectadas")
    for i, f in enumerate(res['frases'][:10], 1):
        try:
            blob_f = TextBlob(f['traducido'])
            emo = '😊' if blob_f.sentiment.polarity > 0.05 else ('😟' if blob_f.sentiment.polarity < -0.05 else '😐')
        except:
            emo = '😐'
        st.write(f"{i}. {emo} Original: \"{f['original']}\"")
        st.write(f"   Traducción: \"{f['traducido']}\"")
        st.write('---')

# Sesión para medir velocidad de escritura
if "typing_start" not in st.session_state:
    st.session_state.typing_start = time.time()

# Lógica principal
if modo == "Texto directo":
    texto = st.text_area("Ingresa tu texto para analizar", key="input_text", height=200)
    if st.button("Analizar texto", key="btn_text"):
        if texto.strip():
            elapsed = time.time() - st.session_state.typing_start
            words = len(texto.split())
            wpm = (words / elapsed) * 60 if elapsed > 0 else 0
            res = procesar_texto(texto)
            crear_visualizaciones(res)
            st.info(f"💨 Velocidad de escritura: {wpm:.2f} palabras por minuto")
        else:
            st.warning("Por favor ingresa algún texto.")
elif modo == "Archivo de texto":
    archivo = st.file_uploader("Selecciona un archivo de texto", type=["txt","csv","md"], key="input_file")
    if archivo is not None:
        contenido = archivo.getvalue().decode('utf-8')
        if st.button("Analizar archivo", key="btn_file"):
            res = procesar_texto(contenido)
            crear_visualizaciones(res)

# Pie de página
st.markdown("---")
st.markdown("Desarrollado con ❤️ usando Streamlit y TextBlob")
