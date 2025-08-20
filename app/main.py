import os
import tempfile
import shutil
from dotenv import load_dotenv
import streamlit as st
from utils.ui import encabezado, mostrar_estado
from logic.ingest import procesar_pdfs, limpiar_almacen_vectores
from logic.retriever import responder_pregunta, obtener_estadisticas_documentos
from logic.chains import resumir_documento, comparar_documentos, clasificar_topicos, obtener_vista_general_documentos

# Configuración de la página
load_dotenv()
PERSIST_DIR = os.environ.get("CHROMA_DIR", "/app/data/chroma")
os.makedirs(PERSIST_DIR, exist_ok=True)

# Configurar página
st.set_page_config(
    page_title="Prueba para CatchAI – Copiloto de Documentos",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar estado de sesión
if 'archivos_subidos' not in st.session_state:
    st.session_state.archivos_subidos = []
if 'documentos_procesados' not in st.session_state:
    st.session_state.documentos_procesados = []
if 'historial_chat' not in st.session_state:
    st.session_state.historial_chat = []

# Función para procesar archivos
def procesar_archivos(archivos):
    """Procesa los archivos PDF subidos."""
    try:
        with st.spinner("🔄 Procesando archivos PDF..."):
            # Crear directorio temporal para archivos
            directorio_temp = tempfile.mkdtemp()
            rutas = []
            
            # Guardar archivos temporalmente
            for archivo in archivos:
                ruta_temp = os.path.join(directorio_temp, archivo.name)
                with open(ruta_temp, "wb") as w:
                    w.write(archivo.read())
                rutas.append(ruta_temp)
            
            # Procesar PDFs
            metadatos = procesar_pdfs(rutas, directorio_persistencia=PERSIST_DIR)
            
            if metadatos:
                # Actualizar estado de sesión
                st.session_state.documentos_procesados = [
                    {
                        'nombre': meta.nombre,
                        'paginas': meta.paginas,
                        'tamaño_mb': meta.tamaño_mb
                    }
                    for meta in metadatos
                ]
                
                st.session_state.archivos_subidos = [
                    {
                        'nombre': archivo.name,
                        'tamaño': archivo.size / (1024 * 1024)
                    }
                    for archivo in archivos
                ]
                
                st.success(f"✅ Procesados {len(metadatos)} documentos exitosamente!")
                st.rerun()
            else:
                st.error("❌ No se pudieron procesar los archivos")
                
    except Exception as e:
        st.error(f"❌ Error procesando archivos: {str(e)}")
    finally:
        # Limpiar archivos temporales
        if 'directorio_temp' in locals():
            shutil.rmtree(directorio_temp, ignore_errors=True)

# Función para limpiar datos
def limpiar_todos_datos():
    """Limpia todos los datos del almacén de vectores."""
    try:
        limpiar_almacen_vectores(PERSIST_DIR)
        st.session_state.documentos_procesados = []
        st.session_state.archivos_subidos = []
        st.session_state.historial_chat = []
        st.success("🗑️ Datos limpiados exitosamente!")
        st.rerun()
    except Exception as e:
        st.error(f"❌ Error limpiando datos: {str(e)}")

# Encabezado principal
encabezado()

# Barra lateral para subida de archivos
with st.sidebar:
    st.subheader("📄 Subir PDFs")
    
    # Límite de archivos
    max_archivos = 5
    archivos = st.file_uploader(
        f"Selecciona hasta {max_archivos} PDFs", 
        type=["pdf"], 
        accept_multiple_files=True,
        key="subidor_pdf"
    )
    
    # Validar límite
    if archivos and len(archivos) > max_archivos:
        st.error(f"⚠️ Máximo {max_archivos} archivos permitidos")
        archivos = archivos[:max_archivos]
    
    # Botones de acción
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Procesar", type="primary", use_container_width=True):
            if archivos:
                procesar_archivos(archivos)
            else:
                st.warning("⚠️ Selecciona archivos PDF primero")
    
    with col2:
        if st.button("🗑️ Limpiar", use_container_width=True):
            limpiar_todos_datos()
    
    # Mostrar archivos subidos
    if st.session_state.archivos_subidos:
        st.markdown("---")
        st.subheader("📋 Archivos subidos")
        for i, info_archivo in enumerate(st.session_state.archivos_subidos):
            st.caption(f"{i+1}. {info_archivo['nombre']} ({info_archivo['tamaño']:.1f}MB)")
    
    # Mostrar documentos procesados
    if st.session_state.documentos_procesados:
        st.markdown("---")
        st.subheader("✅ Documentos procesados")
        for documento in st.session_state.documentos_procesados:
            st.caption(f"• {documento['nombre']} ({documento['paginas']} páginas, {documento['tamaño_mb']}MB)")
    
    # Estadísticas del almacén de vectores
    st.markdown("---")
    st.subheader("📊 Estadísticas")
    estadisticas = obtener_estadisticas_documentos(PERSIST_DIR)
    if estadisticas.get('total_chunks', 0) > 0:
        st.metric("Total de fragmentos", estadisticas['total_chunks'])
        st.metric("Documentos", estadisticas['total_docs'])
    else:
        st.caption("No hay documentos indexados")

# Contenido principal
if st.session_state.documentos_procesados:
    # Vista general de documentos
    with st.expander("📊 Vista General de Documentos", expanded=False):
        vista_general = obtener_vista_general_documentos(PERSIST_DIR)
        st.markdown(vista_general)
    
    # Funcionalidades opcionales
    st.subheader("🔧 Funcionalidades Avanzadas")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**📋 Resumen de Documento**")
        documento_resumen = st.selectbox(
            "Selecciona documento:",
            options=[documento['nombre'] for documento in st.session_state.documentos_procesados],
            key="documento_resumen"
        )
        if st.button("🔎 Generar Resumen", use_container_width=True):
            if documento_resumen:
                with st.spinner("Generando resumen..."):
                    resultado = resumir_documento(documento_resumen, PERSIST_DIR)
                    st.markdown(resultado)
    
    with col2:
        st.markdown("**⚖️ Comparar Documentos**")
        documentos = [documento['nombre'] for documento in st.session_state.documentos_procesados]
        if len(documentos) >= 2:
            documento_a = st.selectbox("Documento A:", options=documentos, key="comparar_a")
            documento_b = st.selectbox("Documento B:", options=documentos, key="comparar_b")
            if st.button("⚖️ Comparar", use_container_width=True):
                if documento_a and documento_b and documento_a != documento_b:
                    with st.spinner("Comparando documentos..."):
                        resultado = comparar_documentos(documento_a, documento_b, PERSIST_DIR)
                        st.markdown(resultado)
                elif documento_a == documento_b:
                    st.warning("⚠️ Selecciona documentos diferentes")
        else:
            st.caption("Se necesitan al menos 2 documentos para comparar")
    
    with col3:
        st.markdown("**🏷️ Clasificación Temática**")
        consulta_tema = st.text_input("Consulta para clasificación:", key="consulta_tema")
        if st.button("🏷️ Clasificar", use_container_width=True):
            if consulta_tema:
                with st.spinner("Clasificando tópicos..."):
                    resultado = clasificar_topicos(consulta_tema, PERSIST_DIR)
                    st.markdown(resultado)
    
    st.markdown("---")

# Chat conversacional
st.subheader("💬 Conversación con Documentos")
st.caption("Haz preguntas sobre el contenido de tus documentos")

# Historial de chat
if st.session_state.historial_chat:
    st.markdown("**📝 Historial de Conversación**")
    for i, (pregunta, respuesta) in enumerate(st.session_state.historial_chat[-5:]):
        with st.expander(f"P{i+1}: {pregunta[:50]}...", expanded=False):
            st.markdown(f"**Pregunta:** {pregunta}")
            st.markdown(f"**Respuesta:** {respuesta}")

# Entrada para preguntas
consulta = st.text_input(
    "Escribe tu pregunta sobre los documentos...",
    placeholder="Ej: ¿Cuáles son los puntos principales del primer documento?",
    key="consulta_usuario"
)

col1, col2 = st.columns([3, 1])
with col1:
    if st.button("🤖 Preguntar", type="primary", use_container_width=True):
        if consulta and consulta.strip():
            if st.session_state.documentos_procesados:
                with st.spinner("🤖 Generando respuesta..."):
                    respuesta = responder_pregunta(consulta, PERSIST_DIR)
                    
                    # Agregar al historial
                    st.session_state.historial_chat.append((consulta, respuesta))
                    
                    # Mostrar respuesta
                    st.markdown("---")
                    st.markdown("**💬 Respuesta:**")
                    st.markdown(respuesta)
                    
                    # Limpiar entrada usando rerun en lugar de modificar estado de sesión
                    st.rerun()
            else:
                st.warning("⚠️ No hay documentos procesados. Sube y procesa algunos PDFs primero.")
        else:
            st.warning("⚠️ Por favor, escribe una pregunta")

with col2:
    if st.button("🗑️ Limpiar Chat", use_container_width=True):
        st.session_state.historial_chat = []
        st.rerun()

# Pie de página
st.markdown("---")
st.caption("🧠 **AI Gemini** - Modelo: Gemini 2.0 Flash + Embeddings open-source + ChromaDB")
st.caption("💡 **Consejo:** Usa preguntas específicas para obtener respuestas más precisas")

# Mostrar estado del sistema
mostrar_estado()
