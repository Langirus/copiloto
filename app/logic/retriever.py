import os
from google import genai
from google.genai import types
from langchain_community.vectorstores import Chroma
from .prompts import PROMPT_SISTEMA, PROMPT_PREGUNTA_RESPUESTA
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def _cliente():
    """Inicializa el cliente de Google Gemini."""
    try:
        # Soporta GOOGLE_API_KEY o GEMINI_API_KEY
        clave_api = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not clave_api:
            raise ValueError("No se encontró GOOGLE_API_KEY o GEMINI_API_KEY en las variables de entorno")
        return genai.Client(api_key=clave_api)
    except Exception as e:
        logger.error(f"Error inicializando cliente Gemini: {e}")
        raise

def cargar_almacen_vectores(directorio_persistencia: str):
    """Carga el almacén de vectores existente."""
    try:
        from langchain_community.embeddings import HuggingFaceEmbeddings
        modelo_embedding = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        embeddings = HuggingFaceEmbeddings(model_name=modelo_embedding)
        
        av = Chroma(collection_name="catchai_docs", 
                    embedding_function=embeddings,
                    persist_directory=directorio_persistencia)
        
        # Verificar que el almacén de vectores tenga contenido
        coleccion = av._collection
        if coleccion.count() == 0:
            logger.warning("Almacén de vectores vacío - no hay documentos indexados")
            return None
            
        return av
    except Exception as e:
        logger.error(f"Error cargando almacén de vectores: {e}")
        return None

def buscar_contexto(av: Chroma, consulta: str, k=5):
    """Busca contexto relevante para una pregunta."""
    try:
        if not av:
            return "No hay documentos indexados para buscar.", []
            
        documentos = av.similarity_search(consulta, k=k)
        if not documentos:
            return "No se encontró contexto relevante para la pregunta.", []
            
        partes_contexto, citas = [], []
        for documento in documentos:
            nombre_doc = documento.metadata.get("doc_name", "doc")
            pagina = documento.metadata.get("page", "?")
            partes_contexto.append(f"[{nombre_doc} p.{pagina}] {documento.page_content}")
            citas.append(f"[{nombre_doc} p.{pagina}]")
            
        return "\n\n".join(partes_contexto), sorted(set(citas))
    except Exception as e:
        logger.error(f"Error en búsqueda de contexto: {e}")
        return "Error buscando contexto.", []

def responder_pregunta(pregunta: str, directorio_persistencia: str):
    """Responde una pregunta usando el contexto de los documentos."""
    try:
        # Validar entrada
        if not pregunta or not pregunta.strip():
            return "❌ Por favor, ingresa una pregunta válida."
            
        # Cargar almacén de vectores
        av = cargar_almacen_vectores(directorio_persistencia)
        if not av:
            return "❌ No hay documentos indexados. Por favor, sube y procesa algunos PDFs primero."
            
        # Buscar contexto
        contexto, citas = buscar_contexto(av, pregunta, k=5)
        if not contexto or contexto == "No hay documentos indexados para buscar.":
            return "❌ No se encontró información relevante para responder tu pregunta."
            
        # Preparar prompt
        sistema = PROMPT_SISTEMA
        usuario = PROMPT_PREGUNTA_RESPUESTA.format(question=pregunta, context=contexto)
        modelo = os.getenv("LLM_MODEL", "gemini-2.0-flash-001")
        
        # Llamar al modelo
        cliente = _cliente()
        
        # Corregir la llamada a Gemini API
        try:
            # Método 1: Usar generate_content con texto simple
            respuesta = cliente.models.generate_content(
                model=modelo,
                contents=f"{sistema}\n\n{usuario}"
            )
        except Exception as e1:
            logger.warning(f"Primer método falló: {e1}")
            try:
                # Método 2: Usar el formato de tipos correcto
                respuesta = cliente.models.generate_content(
                    model=modelo,
                    contents=[types.Content(role="user", parts=[types.Part.from_text(f"{sistema}\n\n{usuario}")])]
                )
            except Exception as e2:
                logger.warning(f"Segundo método falló: {e2}")
                # Método 3: Usar el formato más simple
                respuesta = cliente.models.generate_content(
                    model=modelo,
                    contents=f"{sistema}\n\n{usuario}"
                )
        
        if not respuesta or not respuesta.text:
            return "❌ Error: No se pudo generar una respuesta del modelo."
            
        texto = respuesta.text.strip()
        
        # Agregar fuentes si hay citas
        if citas:
            texto += "\n\n**📚 Fuentes:** " + " ".join(citas)
            
        return texto
        
    except ValueError as e:
        return f"❌ Error de configuración: {e}"
    except Exception as e:
        logger.error(f"Error generando respuesta: {e}")
        return f"❌ Error inesperado: {str(e)}"

def obtener_estadisticas_documentos(directorio_persistencia: str):
    """Obtiene estadísticas del almacén de vectores."""
    try:
        av = cargar_almacen_vectores(directorio_persistencia)
        if not av:
            return {"total_chunks": 0, "documents": []}
            
        coleccion = av._collection
        total_fragmentos = coleccion.count()
        
        # Obtener documentos únicos
        documentos = coleccion.get()
        nombres_documentos = set()
        for metadatos in documentos.get('metadatas', []):
            if metadatos and 'doc_name' in metadatos:
                nombres_documentos.add(metadatos['doc_name'])
                
        return {
            "total_chunks": total_fragmentos,
            "documents": list(nombres_documentos),
            "total_docs": len(nombres_documentos)
        }
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        return {"total_chunks": 0, "documents": [], "error": str(e)}
