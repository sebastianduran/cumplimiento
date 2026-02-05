import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = str(BASE_DIR / "data" / "cumplimiento.db")
SCREENSHOTS_DIR = str(BASE_DIR / "data" / "screenshots")

SUPPORTED_PLATFORMS = {
    "instagram": "instagram.com",
    "facebook": "facebook.com",
    "twitter": "x.com",
    "tiktok": "tiktok.com",
}

DEFAULT_HASHTAGS = ["#BogotaCambia", "#GobiernoDistrital"]
DEFAULT_TONE_KEYWORDS_EMOTIVO = [
    "juntos", "corazon", "orgullo", "suenos", "familia",
    "esperanza", "amor", "comunidad", "transformar", "vida",
]
DEFAULT_TONE_KEYWORDS_INFORMATIVO = [
    "informamos", "comunicado", "resolucion", "decreto",
    "convocatoria", "plazo", "requisitos", "tramite",
]

SCREENSHOT_TIMEOUT_MS = 30000
MAX_CONCURRENT_CAPTURES = 3
GEMINI_MODEL_NAME = "gemini-2.0-flash"
