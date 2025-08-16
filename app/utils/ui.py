import streamlit as st
import os
from datetime import datetime

def encabezado():
    """Encabezado principal de la aplicación."""
    st.title("🧠 CatchAI – Copiloto Conversacional sobre Documentos")
    st.caption("Sube hasta 5 PDFs, haz preguntas y obtén respuestas con contexto inteligente.")
    
    # Mostrar información del sistema
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📊 Estado", "🟢 Activo")
    
    with col2:
        # Verificar clave API
        clave_api = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if clave_api:
            st.metric("🔑 Clave API", "✅ Configurada")
        else:
            st.metric("🔑 Clave API", "❌ Faltante")
    
    with col3:
        # Verificar modelo
        modelo = os.getenv("LLM_MODEL", "gemini-2.0-flash-001")
        st.metric("🤖 Modelo", modelo.split("-")[0].title())

def mostrar_estado():
    """Muestra el estado del sistema."""
    st.markdown("---")
    
    # Información del sistema
    with st.expander("ℹ️ Información del Sistema", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🔧 Configuración**")
            st.caption(f"**Modelo LLM:** {os.getenv('LLM_MODEL', 'gemini-2.0-flash-001')}")
            st.caption(f"**Embeddings:** {os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')}")
            st.caption(f"**Base de Datos Vectorial:** ChromaDB")
            st.caption(f"**Framework:** LangChain")
        
        with col2:
            st.markdown("**📅 Sistema**")
            st.caption(f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            st.caption(f"**Directorio:** {os.getenv('CHROMA_DIR', '/app/data/chroma')}")
            st.caption(f"**Streamlit:** v{st.__version__}")
        
        # Verificar variables de entorno
        st.markdown("**🔑 Variables de Entorno**")
        variables_entorno = {
            "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
            "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
            "EMBEDDING_MODEL": os.getenv("EMBEDDING_MODEL"),
            "LLM_MODEL": os.getenv("LLM_MODEL"),
            "CHROMA_DIR": os.getenv("CHROMA_DIR")
        }
        
        for clave, valor in variables_entorno.items():
            if valor:
                st.caption(f"✅ **{clave}:** Configurada")
            else:
                st.caption(f"❌ **{clave}:** No configurada")

def mostrar_instrucciones_subida():
    """Muestra instrucciones para subir archivos."""
    st.info("""
    **📋 Instrucciones para subir archivos:**
    
    1. **Formato:** Solo archivos PDF
    2. **Límite:** Máximo 5 archivos por sesión
    3. **Tamaño:** Recomendado menos de 50MB por archivo
    4. **Calidad:** PDFs con texto extraíble (no solo imágenes escaneadas)
    5. **Procesamiento:** Los archivos se indexan automáticamente para búsquedas
    
    **💡 Consejo:** Para mejores resultados, usa PDFs con texto nativo en lugar de documentos escaneados.
    """)

def mostrar_consejos_uso():
    """Muestra consejos de uso."""
    st.success("""
    **💡 Consejos para mejores respuestas:**
    
    • **Preguntas específicas:** "¿Cuáles son los objetivos del proyecto en el documento A?"
    • **Comparaciones:** "¿En qué se diferencian los enfoques de los dos documentos?"
    • **Análisis:** "¿Qué riesgos identifica el documento sobre la implementación?"
    • **Síntesis:** "Resume los puntos clave de todos los documentos"
    
    **🔍 Funcionalidades disponibles:**
    • Resumen ejecutivo de documentos
    • Comparación entre documentos
    • Clasificación temática
    • Chat conversacional con contexto
    """)

def mostrar_ayuda_errores():
    """Muestra ayuda para errores comunes."""
    st.warning("""
    **⚠️ Solución de problemas comunes:**
    
    **Error de Clave API:**
    - Verifica que GOOGLE_API_KEY o GEMINI_API_KEY esté configurada
    - Asegúrate de que la clave API sea válida y tenga cuota disponible
    
    **Error de procesamiento:**
    - Verifica que los PDFs no estén corruptos
    - Asegúrate de que los PDFs contengan texto extraíble
    - Intenta con archivos más pequeños
    
    **Error de memoria:**
    - Reduce el número de archivos procesados simultáneamente
    - Usa archivos PDF más pequeños
    - Limpia la base de datos vectorial y vuelve a procesar
    """)
