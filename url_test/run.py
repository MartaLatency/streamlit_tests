import streamlit as st
import requests
import trafilatura
from newspaper import Article
from bs4 import BeautifulSoup
from urllib.parse import urljoin

st.set_page_config(page_title="📰 Lector de artículos", layout="centered")
st.title("📰 Extraer contenido de artículos, vamos, piratear")

# Estado de la app
if "step" not in st.session_state:
    st.session_state.step = 0
if "html_content" not in st.session_state:
    st.session_state.html_content = None
if "url" not in st.session_state:
    st.session_state.url = None

# Entrada de URL
url = st.text_input("Introduce la URL del artículo:", value=st.session_state.url or "")

# Paso 0: Iniciar extracción
if st.button("Extraer artículo"):
    if not url:
        st.warning("⚠️ Por favor, introduce una URL.")
    else:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        response = requests.get(url, headers=headers)
        html_content = response.text
        st.session_state.html_content = html_content
        st.session_state.url = url
        st.session_state.step = 1  # Intentar con Trafilatura

# Paso 1: Trafilatura
if st.session_state.step == 1:
    st.subheader("🧪 Intentando con el método 1...")
    extracted = trafilatura.extract(st.session_state.html_content)
    if extracted:
        st.text_area("Texto extraído:", extracted, height=400)
        choice = st.radio("¿El resultado fue útil?", ["Sí", "No", "Sí, pero quiero descargarlo para verlo mejor"], key="trafilatura_choice")
        if choice == "No":
            st.session_state.step = 2
        elif choice == "Sí, pero quiero descargarlo para verlo mejor":
            st.session_state.step = 3
    else:
        st.warning("Trafilatura no pudo extraer contenido.")
        st.session_state.step = 2

# Paso 2: newspaper3k
if st.session_state.step == 2:
    st.subheader("🧪 Intentando con método 2...")
    try:
        article = Article(st.session_state.url)
        article.download()
        article.parse()
        text = article.text
        if text.strip():
            st.text_area("Texto extraído con newspaper3k:", text, height=400)
            choice = st.radio("¿El resultado fue útil?", ["Sí", "No", "Sí, pero quiero descargarlo para verlo mejor"], key="newspaper_choice")
            if choice == "No":
                st.session_state.step = 3
            elif choice == "Sí, pero quiero descargarlo para verlo mejor":
                st.session_state.step = 3
        else:
            st.warning("newspaper3k no pudo extraer contenido.")
            st.session_state.step = 3
    except Exception as e:
        st.error(f"Error al usar newspaper3k: {e}")
        st.session_state.step = 3

# Paso 3: Descargar HTML completo
if st.session_state.step == 3:
    st.subheader("📄 Descargar HTML completo")

    soup = BeautifulSoup(st.session_state.html_content, "html.parser")
    for tag in soup.find_all(["link", "script", "img"]):
        attr = "href" if tag.name == "link" else "src"
        if tag.has_attr(attr):
            tag[attr] = urljoin(st.session_state.url, tag[attr])

    fixed_html = str(soup)

    st.download_button(
        "📥 Descargar HTML completo",
        data=fixed_html,
        file_name="pagina_completa.html",
        mime="text/html"
    )
    st.info("Puedes abrir el archivo en tu navegador para ver el artículo con estilos e imágenes.")
