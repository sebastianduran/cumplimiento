import base64
from pathlib import Path
from PIL import Image
from io import BytesIO
from config.settings import SCREENSHOTS_DIR


def save_screenshot(post_id: str, image_bytes: bytes) -> str:
    """Guarda screenshot en disco y retorna la ruta."""
    screenshots_dir = Path(SCREENSHOTS_DIR)
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    path = screenshots_dir / f"{post_id}.png"
    path.write_bytes(image_bytes)
    return str(path)


def create_thumbnail(screenshot_path: str, size: tuple[int, int] = (300, 300)) -> str:
    """Crea un thumbnail del screenshot y retorna la ruta."""
    src = Path(screenshot_path)
    if not src.exists():
        return ""

    thumb_path = src.parent / f"{src.stem}_thumb.png"
    try:
        img = Image.open(src)
        img.thumbnail(size, Image.Resampling.LANCZOS)
        img.save(thumb_path, "PNG")
        return str(thumb_path)
    except Exception:
        return ""


def image_to_base64(path: str) -> str:
    """Convierte imagen a base64 para mostrar inline en Streamlit."""
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return ""
