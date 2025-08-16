PROMPT_SISTEMA = """Eres un copiloto conversacional experto en análisis de documentos.
- Responde SOLO con información sustentada en los fragmentos proporcionados.
- Cita las fuentes al final con el formato [Doc N, página X], o [Doc N] si no hay página.
- Si no encuentras soporte suficiente, di claramente que no hay información suficiente en los documentos.
- Sé conciso, estructurado y profesional.
- Usa formato markdown para mejorar la legibilidad."""

PROMPT_PREGUNTA_RESPUESTA = """Pregunta del usuario:
{question}

Contexto relevante (fragmentos de documentos):
{context}

Instrucciones:
- Sintetiza la respuesta usando únicamente el contexto proporcionado.
- Si hay múltiples documentos, integra y compara brevemente la información.
- Devuelve una lista de bullets si la respuesta es larga.
- Mantén un tono profesional y objetivo.

Respuesta:"""

PROMPT_RESUMEN = """Genera un resumen ejecutivo del documento: {doc_name}

Instrucciones:
- Identifica los temas principales y puntos clave
- Destaca hallazgos importantes y conclusiones
- Usa bullets breves (máximo 7 puntos)
- Termina con 2-3 riesgos o limitaciones identificadas
- Mantén un formato ejecutivo profesional

Resumen:"""

PROMPT_COMPARACION = """Compara los documentos: {doc_a} vs {doc_b}

Instrucciones:
- Analiza objetivos clave de cada documento
- Identifica hallazgos y conclusiones principales
- Evalúa supuestos y riesgos
- Destaca coincidencias y diferencias significativas
- Termina con una síntesis comparativa de 2 líneas

Comparación:"""

PROMPT_CLASIFICACION_TEMATICA = """Clasifica los tópicos relacionados con la consulta: {query}

Instrucciones:
- Identifica y categoriza los temas principales
- Agrupa conceptos relacionados
- Asigna prioridad o relevancia a cada tópico
- Sugiere posibles subtópicos o áreas de investigación
- Proporciona una estructura jerárquica de temas

Clasificación temática:"""

PROMPT_ANALISIS_DOCUMENTO = """Analiza el documento: {doc_name}

Instrucciones:
- Identifica el tipo de documento y su propósito
- Extrae información clave: fechas, entidades, métricas
- Identifica el público objetivo
- Destaca hallazgos principales
- Sugiere preguntas de seguimiento relevantes

Análisis:"""
