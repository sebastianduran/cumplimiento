import re
from urllib.parse import urlparse
import pandas as pd
from core.models import Platform
from config.settings import SUPPORTED_PLATFORMS


def validate_url(url: str) -> bool:
    try:
        result = urlparse(url.strip())
        return all([result.scheme in ("http", "https"), result.netloc])
    except Exception:
        return False


def detect_platform(url: str) -> Platform:
    url_lower = url.lower()
    for platform, domain in SUPPORTED_PLATFORMS.items():
        if domain in url_lower:
            return Platform(platform)
    return Platform.UNKNOWN


def parse_url_file(uploaded_file) -> list[str]:
    """Lee un archivo CSV o Excel y extrae URLs de la primera columna."""
    try:
        filename = uploaded_file.name.lower()
        if filename.endswith(".csv"):
            df = pd.read_csv(uploaded_file, header=None)
        elif filename.endswith((".xlsx", ".xls")):
            df = pd.read_excel(uploaded_file, header=None)
        else:
            return []

        urls = []
        for val in df.iloc[:, 0]:
            val_str = str(val).strip()
            if validate_url(val_str):
                urls.append(val_str)
        return urls
    except Exception:
        return []


def clean_url(url: str) -> str:
    """Limpia y normaliza una URL."""
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url
