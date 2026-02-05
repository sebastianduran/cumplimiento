import json
import re
from typing import Callable, Optional, Protocol
from analysis.prompts import build_compliance_prompt
from core.models import AnalysisResult, PostResult, ComplianceStatus, ComplianceConfig


def _extract_json(text: str) -> dict:
    """Extrae un objeto JSON de la respuesta del modelo, sin importar texto extra.

    Intenta multiples estrategias:
    1. Parsear directamente como JSON
    2. Extraer bloque ```json ... ```
    3. Buscar el primer { ... } balanceado en el texto
    """
    text = text.strip()

    # Estrategia 1: JSON directo
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Estrategia 2: Extraer bloque markdown ```json ... ```
    match = re.search(r"```(?:json)?\s*\n?(.*?)\n?\s*```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # Estrategia 3: Buscar el primer objeto JSON { ... } balanceado
    start = text.find("{")
    if start != -1:
        depth = 0
        for i in range(start, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start:i + 1])
                    except json.JSONDecodeError:
                        break

    raise json.JSONDecodeError("No se encontro JSON valido en la respuesta", text, 0)


class VisionClient(Protocol):
    """Interfaz comun para clientes de vision (Gemini, Ollama, etc.)."""
    def analyze_image_and_text(self, image_bytes: bytes, prompt: str) -> str: ...


def create_vision_client(config: ComplianceConfig) -> VisionClient:
    """Crea el cliente de vision segun la configuracion."""
    if config.ai_backend.value == "ollama":
        from analysis.ollama_client import OllamaClient
        return OllamaClient(
            model_name=config.ollama_model,
            base_url=config.ollama_url,
        )
    else:
        import os
        from analysis.gemini_client import GeminiClient
        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            raise ValueError("GEMINI_API_KEY no esta configurada en el archivo .env")
        return GeminiClient(
            api_key=api_key,
            model_name=config.gemini_model,
        )


class ComplianceAnalyzer:
    """Orquestador de analisis: envia screenshots al modelo de vision y parsea resultados."""

    def __init__(self, vision_client: VisionClient):
        self.client = vision_client

    def analyze_post(self, post: PostResult, config: ComplianceConfig) -> PostResult:
        """Analiza un post capturado contra la configuracion de cumplimiento."""
        if post.status == ComplianceStatus.ERROR:
            return post

        if not post.screenshot_path:
            post.status = ComplianceStatus.ERROR
            post.error_message = "No hay screenshot disponible para analizar"
            return post

        prompt = build_compliance_prompt(
            config.required_hashtags,
            config.emotional_keywords,
            config.brand_guidelines_notes,
        )

        full_prompt = f"{prompt}\n\nTexto extraido del post:\n{post.extracted_text}"

        raw_response = ""
        try:
            with open(post.screenshot_path, "rb") as f:
                image_bytes = f.read()

            raw_response = self.client.analyze_image_and_text(image_bytes, full_prompt)

            parsed = _extract_json(raw_response)

            analysis = AnalysisResult(
                hashtags_present=parsed.get("hashtags_encontrados", []),
                hashtags_missing=parsed.get("hashtags_faltantes", []),
                emotional_score=float(parsed.get("puntaje_emotivo", 0.0)),
                tone_label=parsed.get("etiqueta_tono", "informativo"),
                brand_identity=parsed.get("identidad_marca", False),
                design_errors=parsed.get("errores_diseno", []),
                common_errors=parsed.get("errores_comunes", []),
                suggested_corrections=parsed.get("correcciones_sugeridas", []),
                raw_ai_response=raw_response,
            )
            post.analysis = analysis

            # Determinar cumplimiento general
            has_errors = (
                len(analysis.hashtags_missing) > 0
                or not analysis.brand_identity
                or len(analysis.design_errors) > 0
            )
            post.status = ComplianceStatus.NO_CUMPLE if has_errors else ComplianceStatus.CUMPLE

        except json.JSONDecodeError:
            post.analysis = AnalysisResult(raw_ai_response=raw_response)
            post.status = ComplianceStatus.ERROR
            preview = raw_response[:200] if raw_response else "(vacio)"
            post.error_message = f"No se pudo parsear la respuesta de la IA. Preview: {preview}"
        except Exception as e:
            post.status = ComplianceStatus.ERROR
            post.error_message = f"Error en analisis: {str(e)}"

        return post

    def analyze_batch(
        self,
        posts: list[PostResult],
        config: ComplianceConfig,
        progress_callback: Optional[Callable] = None,
    ) -> list[PostResult]:
        """Analiza un batch de posts con reporte de progreso."""
        results = []
        for i, post in enumerate(posts):
            result = self.analyze_post(post, config)
            results.append(result)
            if progress_callback:
                progress_callback(
                    (i + 1) / len(posts),
                    f"Analizando {i + 1}/{len(posts)}...",
                )
        return results
