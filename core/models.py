from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class Platform(str, Enum):
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    TIKTOK = "tiktok"
    UNKNOWN = "unknown"


class ComplianceStatus(str, Enum):
    CUMPLE = "cumple"
    NO_CUMPLE = "no-cumple"
    PENDIENTE = "pendiente"
    ERROR = "error"


class AnalysisResult(BaseModel):
    hashtags_present: list[str] = []
    hashtags_missing: list[str] = []
    emotional_score: float = 0.0
    tone_label: str = "informativo"
    brand_identity: bool = False
    design_errors: list[str] = []
    common_errors: list[str] = []
    suggested_corrections: list[str] = []
    raw_ai_response: str = ""


class PostResult(BaseModel):
    post_id: str
    url: str
    platform: Platform
    status: ComplianceStatus = ComplianceStatus.PENDIENTE
    extracted_text: str = ""
    screenshot_path: str = ""
    thumbnail_path: str = ""
    analysis: Optional[AnalysisResult] = None
    created_at: datetime = datetime.now()
    error_message: str = ""
    batch_id: str = ""


class AIBackend(str, Enum):
    GEMINI = "gemini"
    OLLAMA = "ollama"


class ComplianceConfig(BaseModel):
    required_hashtags: list[str] = []
    emotional_keywords: list[str] = []
    informational_keywords: list[str] = []
    brand_guidelines_notes: str = ""
    ai_backend: AIBackend = AIBackend.GEMINI
    ollama_model: str = "llama3.2-vision"
    ollama_url: str = "http://localhost:11434"
    gemini_model: str = "gemini-2.0-flash"
