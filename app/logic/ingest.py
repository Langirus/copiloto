import os, re
from dataclasses import dataclass
from typing import List, Tuple, Optional
from pypdf import PdfReader
import pdfplumber
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
import tempfile
import shutil

@dataclass
class MetadatosDocumento:
    id_documento: int
    nombre: str
    paginas: int
    tamaño_mb: float

def extraer_texto_pdf(ruta: str) -> List[Tuple[str,int]]:
    """Devuelve lista de (texto, pagina)."""
    textos = []
    try:
        with pdfplumber.open(ruta) as pdf:
            for i, pagina in enumerate(pdf.pages, start=1):
                texto = pagina.extract_text() or ""
                # Normalización básica
                texto = re.sub(r'\s+', ' ', texto).strip()
                if texto:  # Solo agregar páginas con contenido
                    textos.append((texto, i))
    except Exception as e:
        print(f"Error procesando {ruta}: {e}")
        return []
    return textos

def fragmentar_documentos(paginas_texto: List[Tuple[str,int]], tamaño_fragmento=900, superposicion_fragmento=150):
    if not paginas_texto:
        return []
    
    divisor = RecursiveCharacterTextSplitter(
        chunk_size=tamaño_fragmento, chunk_overlap=superposicion_fragmento,
        separators=["\n\n", "\n", ". ", " "]
    )
    fragmentos = []
    for texto, pagina in paginas_texto:
        if len(texto.strip()) > 50:  # Solo fragmentos con contenido significativo
            for fragmento in divisor.split_text(texto):
                if len(fragmento.strip()) > 20:  # Filtrar fragmentos muy pequeños
                    fragmentos.append((fragmento.strip(), pagina))
    return fragmentos

def construir_almacen_vectores(documentos: List[Tuple[str,int]], metadatos_base: dict, directorio_persistencia: str, nombre_coleccion: str = "catchai_docs"):
    """Construye o actualiza el almacén de vectores."""
    modelo_embedding = os.environ.get("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    embeddings = HuggingFaceEmbeddings(model_name=modelo_embedding)

    if not documentos:
        print("No hay documentos para procesar")
        return None

    textos, metadatos = [], []
    for texto, pagina in documentos:
        textos.append(texto)
        md = {**metadatos_base, "pagina": pagina}
        metadatos.append(md)

    try:
        # Intentar cargar almacén de vectores existente
        av = Chroma(collection_name=nombre_coleccion,
                    embedding_function=embeddings,
                    persist_directory=directorio_persistencia)
        
        # Agregar nuevos textos
        av.add_texts(texts=textos, metadatas=metadatos)
        av.persist()
        print(f"✅ Agregados {len(textos)} fragmentos al almacén de vectores")
        return av
    except Exception as e:
        print(f"Error con almacén de vectores existente, creando nuevo: {e}")
        # Crear nuevo almacén de vectores
        av = Chroma.from_texts(
            texts=textos,
            metadatas=metadatos,
            embedding=embeddings,
            collection_name=nombre_coleccion,
            persist_directory=directorio_persistencia
        )
        av.persist()
        return av

def procesar_pdfs(rutas: List[str], directorio_persistencia: str) -> List[MetadatosDocumento]:
    """Procesa múltiples PDFs y retorna metadatos."""
    metadatos = []
    
    # Asegurar que el directorio existe
    os.makedirs(directorio_persistencia, exist_ok=True)
    
    # Procesar cada PDF
    for i, ruta_pdf in enumerate(rutas, start=1):
        try:
            if not os.path.exists(ruta_pdf):
                print(f"⚠️ Archivo no encontrado: {ruta_pdf}")
                continue
                
            # Obtener tamaño del archivo
            tamaño_mb = os.path.getsize(ruta_pdf) / (1024 * 1024)
            
            print(f"📄 Procesando: {os.path.basename(ruta_pdf)}")
            paginas = extraer_texto_pdf(ruta_pdf)
            
            if not paginas:
                print(f"⚠️ No se pudo extraer texto de: {ruta_pdf}")
                continue
                
            fragmentos = fragmentar_documentos(paginas)
            if not fragmentos:
                print(f"⚠️ No se generaron fragmentos válidos de: {ruta_pdf}")
                continue
                
            # Construir almacén de vectores
            av = construir_almacen_vectores(
                documentos=fragmentos,
                metadatos_base={"id_documento": i, "nombre_documento": os.path.basename(ruta_pdf)},
                directorio_persistencia=directorio_persistencia
            )
            
            if av:
                meta = MetadatosDocumento(
                    id_documento=i,
                    nombre=os.path.basename(ruta_pdf),
                    paginas=len(paginas),
                    tamaño_mb=round(tamaño_mb, 2)
                )
                metadatos.append(meta)
                print(f"✅ Procesado: {meta.nombre} ({meta.paginas} páginas, {meta.tamaño_mb}MB)")
            else:
                print(f"❌ Error procesando: {ruta_pdf}")
                
        except Exception as e:
            print(f"❌ Error procesando {ruta_pdf}: {e}")
            continue
    
    return metadatos

def limpiar_almacen_vectores(directorio_persistencia: str, nombre_coleccion: str = "catchai_docs"):
    """Limpia el almacén de vectores existente."""
    try:
        if os.path.exists(directorio_persistencia):
            shutil.rmtree(directorio_persistencia)
            print("🗑️ Almacén de vectores limpiado")
    except Exception as e:
        print(f"Error limpiando almacén de vectores: {e}")
