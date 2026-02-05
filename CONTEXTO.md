la prioridad absoluta es la usabilidad y la automatización del análisis posterior. El usuario solo debe "pegar y ver resultados".

Skill: Social Compliance Monitor (Distrital)
Contexto del Agente
Eres un experto en Full-Stack Development (Python/Streamlit) y Visión Artificial. Tu objetivo es construir una interfaz limpia que permita a un usuario administrativo cargar URLs de redes sociales, procesarlas visualmente y recibir un reporte automático de cumplimiento de marca.

1. Interfaz de Usuario (UX/UI)
Carga Dual: Un campo de texto para una sola URL y un botón de "Upload" para archivos CSV/Excel con múltiples URLs.

Dashboard de Visualización: Una tabla dinámica que muestre:

Miniatura del post (screenshot).

Texto extraído.

Semáforo de cumplimiento (Verde: Cumple / Rojo: Error).

Panel de Configuración: Donde el usuario define los hashtags obligatorios y las palabras clave del "tono emotivo".

2. Requerimientos Técnicos del Skill
A. Módulo de Extracción (Scraper/Snapshot)
Utilizar Playwright para renderizar las URLs de Instagram, Facebook, X y TikTok.

Función capture_content(url):

Detectar el contenedor del post.

Tomar captura de pantalla (JPG/PNG).

Extraer el texto plano del cuerpo del mensaje.

B. Módulo de Análisis (IA Engine)
Integrar con una API de modelo de lenguaje con visión (ej. GPT-4o o Gemini Pro Vision).

Prompt de Análisis: > "Analiza esta imagen y texto de una entidad distrital. 1. ¿Aparece el logo oficial? 2. ¿Usa los hashtags [X, Y]? 3. ¿El tono es emotivo o puramente informativo? 4. Identifica errores de diseño según el manual de marca."

C. Módulo de Reportes
Generar un resumen de "Errores más comunes" (Ej: "El 40% de los posts no usan el hashtag de la campaña").

Botón para exportar el reporte final en PDF o Excel.

3. Lógica de Flujo de Trabajo
Input: Usuario carga lista de URLs.

Proceso: El sistema recorre la lista, toma capturas y extrae texto en segundo plano.

Evaluación: La IA compara cada post contra los lineamientos guardados.

Output: Se despliega una galería de tarjetas (Cards) con el análisis individual y las correcciones sugeridas.

4. Estructura de Datos Sugerida
JSON
{
  "post_id": "string",
  "url": "string",
  "status": "cumple/no-cumple",
  "extracted_text": "string",
  "analysis": {
    "hashtags_present": ["list"],
    "emotional_score": "float",
    "brand_identity": "boolean",
    "common_errors": ["list"]
  }
}

¿Cómo funciona este prototipo para el usuario?
Carga Masiva: El usuario arrastra su Excel con 100 URLs.

Procesamiento Transparente: Mientras el código de Playwright (en el backend) navega y toma las capturas, el usuario ve una barra de progreso real.

Validación Visual: En lugar de solo ver texto, el usuario ve la "Foto" de lo que publicó la entidad al lado de la corrección.

Reporte de Errores: Al final, el gráfico de barras le dice qué es lo que más está fallando en la comunicación distrital para tomar decisiones.

