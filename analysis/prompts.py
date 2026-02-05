def build_compliance_prompt(
    required_hashtags: list[str],
    emotional_keywords: list[str],
    brand_notes: str,
) -> str:
    hashtags_str = ", ".join(required_hashtags) if required_hashtags else "ninguno definido"
    keywords_str = ", ".join(emotional_keywords) if emotional_keywords else "ninguno definido"

    return f"""Analiza esta imagen y el texto de una publicacion de una entidad distrital.
Responde en formato JSON estricto con la siguiente estructura (sin markdown, sin bloques de codigo, solo el JSON puro):

{{
  "logo_oficial_presente": true o false,
  "hashtags_encontrados": ["lista de hashtags presentes en el post"],
  "hashtags_faltantes": ["lista de hashtags obligatorios que NO aparecen"],
  "puntaje_emotivo": 0.0 a 1.0,
  "etiqueta_tono": "emotivo" o "informativo",
  "identidad_marca": true o false,
  "errores_diseno": ["lista de errores de diseno detectados"],
  "errores_comunes": ["lista de errores generales de comunicacion"],
  "correcciones_sugeridas": ["lista de correcciones recomendadas"]
}}

Lineamientos a evaluar:
- Hashtags obligatorios: {hashtags_str}
- Palabras clave de tono emotivo esperado: {keywords_str}
- Notas del manual de marca: {brand_notes if brand_notes else "No proporcionadas"}

Reglas de evaluacion:
1. Si el logo oficial de la entidad distrital es visible, marca logo_oficial_presente como true.
2. Compara los hashtags del post con los hashtags obligatorios listados arriba.
3. Evalua si el tono del mensaje es emotivo o informativo segun las palabras clave.
4. El puntaje_emotivo va de 0.0 (puramente informativo) a 1.0 (altamente emotivo).
5. Identifica errores de diseno segun lineamientos institucionales (uso de colores, tipografia, composicion).
6. En errores_comunes incluye problemas frecuentes como: falta de hashtags, mala calidad de imagen, texto ilegible, etc.
7. Las correcciones_sugeridas deben ser accionables y especificas.
8. Responde UNICAMENTE con el JSON, sin texto adicional, sin bloques de codigo markdown."""
