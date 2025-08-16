# 🧠 Prueba para CatchAI – Copiloto Conversacional sobre Documentos

Un copiloto conversacional inteligente que permite analizar y hacer preguntas sobre múltiples documentos PDF usando IA avanzada.

## ✨ Características

### 🎯 Funcionalidades Principales
- **Subida de hasta 5 archivos PDF** simultáneamente
- **Extracción y vectorización inteligente** del contenido
- **Chat conversacional** con contexto de documentos
- **Búsqueda semántica** usando embeddings avanzados
- **Respuestas contextuales** basadas en el contenido real

### 🔧 Funcionalidades Avanzadas
- **Resumen ejecutivo** de documentos individuales
- **Comparación automática** entre documentos
- **Clasificación temática** inteligente
- **Vista general** de todos los documentos indexados
- **Historial de conversación** persistente

### 🛠️ Tecnologías
- **LLM**: Google gemini-2.0-flash 
- **Embeddings**: Sentence Transformers (open-source)
- **Base de Datos Vectorial**: ChromaDB
- **Framework**: LangChain
- **Interfaz**: Streamlit
- **Contenedores**: Docker + Docker Compose

## 🚀 Instalación Rápida


### 1. Configurar variables de entorno
```bash
# Copiar el archivo de ejemplo
cp env.example .env

# Editar .env con tu clave API de Google
GOOGLE_API_KEY=tu_clave_api_google_aqui
```

### 2. Ejecutar con Docker (Recomendado)
```bash
# Construir y ejecutar en terminal.Recordar de tener descargado e iniciado Docker
docker-compose up --build

# La aplicación estará disponible en: http://localhost:8501
# Para detener la ejecución colocar en terminal Ctrl+c
```


## 🔑 Configuración

### Variables de Entorno Requeridas

|     Variable     |        Descripción         |             Valor por Defecto            |
|------------------|----------------------------|------------------------------------------|
| `GOOGLE_API_KEY` | Clave API de Google Gemini |               ----------                 |
| `LLM_MODEL`      | Modelo de lenguaje         | `gemini-2.0-flash-001`                   |
| `EMBEDDING_MODEL`| Modelo de embeddings       | `sentence-transformers/all-MiniLM-L6-v2` |
| `CHROMA_DIR`     | Directorio de ChromaDB     | `/app/data/chroma`                       |


### Obtener Clave API de Google

1. Ve a [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Crea una nueva clave API
3. Copia la clave en tu archivo `.env`

## 📖 Uso

### 1. Subir Documentos
- Usa la barra lateral para subir hasta 5 archivos PDF
- Los archivos se procesan automáticamente
- Se extrae texto, se dividen en fragmentos y se vectorizan

### 2. Hacer Preguntas
- Escribe preguntas en lenguaje natural
- El sistema busca contexto relevante en los documentos
- Obtén respuestas con citas de fuentes

### 3. Funcionalidades Avanzadas
- **Resumen**: Genera resúmenes ejecutivos de documentos
- **Comparación**: Compara contenido entre documentos
- **Clasificación**: Clasifica tópicos por consulta

## 🏗️ Arquitectura

### 📁 Estructura Completa del Proyecto

```
copiloto/
├── 📁 app/                    # Código fuente principal
│   ├── 📄 __init__.py         # Inicialización del paquete
│   ├── 📄 main.py             # Aplicación principal (procesar_archivos, limpiar_todos_datos)
│   ├── 📁 logic/              # Lógica de negocio
│   │   ├── 📄 __init__.py     # Inicialización de lógica
│   │   ├── 📄 ingest.py       # Procesamiento de PDFs (procesar_pdfs, extraer_texto_pdf)
│   │   ├── 📄 retriever.py    # Búsqueda y respuestas (responder_pregunta, buscar_contexto)
│   │   ├── 📄 chains.py       # Funcionalidades avanzadas (resumir_documento, comparar_documentos)
│   │   └── 📄 prompts.py      # Prompts del sistema (PROMPT_SISTEMA, PROMPT_RESUMEN)
│   └── 📁 utils/              # Utilidades
│       ├── 📄 __init__.py     # Inicialización de utilidades
│       └── 📄 ui.py           # Componentes de interfaz (encabezado, mostrar_estado)
├── 📁 data/                    # Datos persistentes (ChromaDB)
├── 📁 .streamlit/             # Configuración de Streamlit
│   └── 📄 config.toml         # Configuración específica de la aplicación
├── 📄 .env.example            # Variables de entorno de ejemplo
├── 📄 .gitignore              # Archivos a ignorar en Git
├── 📄 Dockerfile              # Instrucciones para construir imagen Docker
├── 📄 docker-compose.yml      # Orquestación de contenedores Docker
├── 📄 pyproject.toml          # Metadatos y configuración del proyecto
├── 📄 README.md               # Documentación principal del proyecto
└── 📄 requirements.txt        # Dependencias Python del proyecto
```

### 🔧 Componentes por Capa

#### **🎯 Capa de Presentación (UI)**
- **`app/main.py`**: Página principal de Streamlit, gestión de estado y navegación
- **`app/utils/ui.py`**: Componentes reutilizables de interfaz (encabezados, métricas, instrucciones)

#### **🧠 Capa de Lógica de Negocio**
- **`app/logic/ingest.py`**: Procesamiento de PDFs, extracción de texto, fragmentación y vectorización
- **`app/logic/retriever.py`**: Búsqueda semántica, recuperación de contexto y generación de respuestas
- **`app/logic/chains.py`**: Funcionalidades avanzadas (resúmenes, comparaciones, clasificación temática)
- **`app/logic/prompts.py`**: Templates de prompts para el modelo de lenguaje

#### **🗄️ Capa de Datos**
- **`data/`**: Almacenamiento persistente de ChromaDB y documentos procesados
- **`app/logic/ingest.py`**: Gestión de metadatos y persistencia de vectores

#### **🐳 Capa de Despliegue**
- **`Dockerfile`**: Instrucciones para crear la imagen de la aplicación
- **`docker-compose.yml`**: Orquestación de la aplicación y sus dependencias
- **`.streamlit/config.toml`**: Configuración específica de Streamlit

#### **⚙️ Capa de Configuración**
- **`.env.example`**: Plantilla de variables de entorno necesarias
- **`requirements.txt`**: Dependencias Python del proyecto
- **`pyproject.toml`**: Metadatos, configuración y dependencias del proyecto
- **`.gitignore`**: Control de versiones y archivos a ignorar

### Flujo de Procesamiento
1. **Ingestión**: PDF → Texto → Fragmentos → Embeddings → ChromaDB
2. **Búsqueda**: Consulta → Embedding → Búsqueda por Similitud → Contexto
3. **Respuesta**: Contexto + Consulta → LLM → Respuesta + Fuentes

## 🔧 Personalización

### Cambiar Modelo de Embeddings
```python
# En .env
EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2
```

### Cambiar Modelo de LLM
```python
# En .env
LLM_MODEL=gemini-2.0-flash
```

### Ajustar Tamaño de Fragmentos
```python
# En app/logic/ingest.py
def fragmentar_documentos(paginas_texto, tamaño_fragmento=900, superposicion_fragmento=150):
```

## 🐛 Solución de Problemas

### Error de Clave API
- Verifica que `GOOGLE_API_KEY` esté configurada en `.env`
- Asegúrate de que la clave API sea válida y tenga cuota

### Error de Procesamiento de PDFs
- Verifica que los PDFs no estén corruptos
- Asegúrate de que contengan texto extraíble (no solo imágenes)
- Intenta con archivos más pequeños

### Problemas de Memoria
- Reduce el número de archivos procesados simultáneamente
- Usa archivos PDF más pequeños
- Limpia el almacén de vectores y vuelve a procesar

## 📊 Rendimiento

### Límites Recomendados
- **Archivos**: Máximo 5 PDFs por sesión
- **Tamaño**: Menos de 50MB por archivo
- **Páginas**: Hasta 100 páginas por documento
- **Fragmentos**: ~1000 fragmentos por documento

### Optimizaciones
- Los embeddings se cachean automáticamente
- ChromaDB persiste los datos entre sesiones
- Procesamiento asíncrono de archivos grandes



## 🙏 Agradecimientos

- [Google Gemini](https://ai.google.dev/) por el modelo de lenguaje
- [LangChain](https://www.langchain.com/) por el framework de orquestación
- [ChromaDB](https://www.trychroma.com/) por la base de datos vectorial
- [Streamlit](https://streamlit.io/) por la interfaz web



