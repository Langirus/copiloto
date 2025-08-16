import os
from google import genai
from google.genai import types
from .prompts import PROMPT_RESUMEN, PROMPT_COMPARACION, PROMPT_CLASIFICACION_TEMATICA
from .retriever import cargar_almacen_vectores, buscar_contexto
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def _cliente():
    """Inicializa el cliente de Google Gemini."""
    try:
        clave_api = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not clave_api:
            raise ValueError("No se encontró GOOGLE_API_KEY o GEMINI_API_KEY en las variables de entorno")
        return genai.Client(api_key=clave_api)
    except Exception as e:
        logger.error(f"Error inicializando cliente Gemini: {e}")
        raise

def _llamar_modelo(modelo, texto):
    """Llama al modelo Gemini con manejo de errores."""
    try:
        cliente = _cliente()
        
        # Corregir la llamada a Gemini API
        try:
            # Método 1: Usar generate_content con texto simple
            respuesta = cliente.models.generate_content(
                model=modelo,
                contents=texto
            )
        except Exception as e1:
            logger.warning(f"Primer método falló: {e1}")
            try:
                # Método 2: Usar el formato de tipos correcto
                respuesta = cliente.models.generate_content(
                    model=modelo,
                    contents=[types.Content(role="user", parts=[types.Part.from_text(texto)])]
                )
            except Exception as e2:
                logger.warning(f"Segundo método falló: {e2}")
                # Método 3: Usar el formato más simple
                respuesta = cliente.models.generate_content(
                    model=modelo,
                    contents=texto
                )
        
        return (respuesta.text or "").strip()
    except Exception as e:
        logger.error(f"Error llamando al modelo: {e}")
        return f"❌ Error generando respuesta: {str(e)}"

def resumir_documento(nombre_documento, directorio_persistencia):
    """Genera un resumen ejecutivo de un documento."""
    try:
        if not nombre_documento or not nombre_documento.strip():
            return "❌ Por favor, especifica el nombre del documento a resumir."
            
        av = cargar_almacen_vectores(directorio_persistencia)
        if not av:
            return "❌ No hay documentos indexados. Por favor, sube y procesa algunos PDFs primero."
            
        # Buscar contexto relevante del documento
        contexto, _ = buscar_contexto(av, f"Temas principales del documento {nombre_documento}", k=8)
        if not contexto or contexto == "No hay documentos indexados para buscar.":
            return f"❌ No se encontró información del documento '{nombre_documento}'."
            
        prompt = PROMPT_RESUMEN.format(doc_name=nombre_documento) + f"\n\nContexto:\n{contexto}\n"
        modelo = os.getenv("LLM_MODEL", "gemini-2.0-flash-001")
        
        resultado = _llamar_modelo(modelo, prompt)
        if resultado.startswith("❌"):
            return resultado
            
        return f"**📋 Resumen de {nombre_documento}**\n\n{resultado}"
        
    except Exception as e:
        logger.error(f"Error resumiendo documento: {e}")
        return f"❌ Error inesperado: {str(e)}"

def comparar_documentos(documento_a, documento_b, directorio_persistencia):
    """Compara dos documentos."""
    try:
        if not documento_a or not documento_b or not documento_a.strip() or not documento_b.strip():
            return "❌ Por favor, especifica ambos documentos para comparar."
            
        if documento_a == documento_b:
            return "❌ No puedes comparar un documento consigo mismo."
            
        av = cargar_almacen_vectores(directorio_persistencia)
        if not av:
            return "❌ No hay documentos indexados. Por favor, sube y procesa algunos PDFs primero."
            
        # Buscar contexto de ambos documentos
        contexto_a, _ = buscar_contexto(av, f"Temas claves de {documento_a}", k=6)
        contexto_b, _ = buscar_contexto(av, f"Temas claves de {documento_b}", k=6)
        
        if not contexto_a or contexto_a == "No hay documentos indexados para buscar.":
            return f"❌ No se encontró información del documento '{documento_a}'."
        if not contexto_b or contexto_b == "No hay documentos indexados para buscar.":
            return f"❌ No se encontró información del documento '{documento_b}'."
            
        prompt = PROMPT_COMPARACION.format(doc_a=documento_a, doc_b=documento_b) + \
                 f"\n\nContexto {documento_a}:\n{contexto_a}\n\nContexto {documento_b}:\n{contexto_b}\n"
        
        modelo = os.getenv("LLM_MODEL", "gemini-2.0-flash-001")
        resultado = _llamar_modelo(modelo, prompt)
        
        if resultado.startswith("❌"):
            return resultado
            
        return f"**⚖️ Comparación: {documento_a} vs {documento_b}**\n\n{resultado}"
        
    except Exception as e:
        logger.error(f"Error comparando documentos: {e}")
        return f"❌ Error inesperado: {str(e)}"

def clasificar_topicos(consulta, directorio_persistencia):
    """Clasifica tópicos basado en una consulta."""
    try:
        if not consulta or not consulta.strip():
            return "❌ Por favor, especifica una consulta para la clasificación temática."
            
        av = cargar_almacen_vectores(directorio_persistencia)
        if not av:
            return "❌ No hay documentos indexados. Por favor, sube y procesa algunos PDFs primero."
            
        # Buscar contexto relevante para la consulta
        contexto, _ = buscar_contexto(av, consulta, k=10)
        if not contexto or contexto == "No hay documentos indexados para buscar.":
            return "❌ No se encontró información relevante para la consulta."
            
        prompt = PROMPT_CLASIFICACION_TEMATICA.format(query=consulta) + f"\n\nContexto:\n{contexto}\n"
        modelo = os.getenv("LLM_MODEL", "gemini-2.0-flash-001")
        
        resultado = _llamar_modelo(modelo, prompt)
        if resultado.startswith("❌"):
            return resultado
            
        return f"**🏷️ Clasificación Temática**\n\n**Consulta:** {consulta}\n\n{resultado}"
        
    except Exception as e:
        logger.error(f"Error clasificando tópicos: {e}")
        return f"❌ Error inesperado: {str(e)}"

def obtener_vista_general_documentos(directorio_persistencia):
    """Obtiene una vista general de todos los documentos."""
    try:
        av = cargar_almacen_vectores(directorio_persistencia)
        if not av:
            return "❌ No hay documentos indexados."
            
        # Obtener estadísticas básicas
        coleccion = av._collection
        total_fragmentos = coleccion.count()
        
        # Obtener documentos únicos
        documentos = coleccion.get()
        estadisticas_documentos = {}
        for metadatos in documentos.get('metadatas', []):
            if metadatos and 'doc_name' in metadatos:
                nombre_documento = metadatos['doc_name']
                if nombre_documento not in estadisticas_documentos:
                    estadisticas_documentos[nombre_documento] = {'paginas': set(), 'fragmentos': 0}
                estadisticas_documentos[nombre_documento]['paginas'].add(metadatos.get('page', 0))
                estadisticas_documentos[nombre_documento]['fragmentos'] += 1
        
        if not estadisticas_documentos:
            return "❌ No se encontraron documentos en el índice."
            
        vista_general = f"**📊 Vista General de Documentos**\n\n"
        vista_general += f"**Total de fragmentos:** {total_fragmentos}\n"
        vista_general += f"**Documentos indexados:** {len(estadisticas_documentos)}\n\n"
        
        for nombre_documento, estadisticas in estadisticas_documentos.items():
            paginas = len(estadisticas['paginas'])
            fragmentos = estadisticas['fragmentos']
            vista_general += f"• **{nombre_documento}**: {paginas} páginas, {fragmentos} fragmentos\n"
            
        return vista_general
        
    except Exception as e:
        logger.error(f"Error obteniendo vista general: {e}")
        return f"❌ Error obteniendo vista general: {str(e)}"
